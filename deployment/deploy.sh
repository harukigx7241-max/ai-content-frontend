#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# deploy.sh — プロンプトギルド VPS デプロイ / アップデートスクリプト
#
# 初回セットアップ: bash deployment/deploy.sh --setup
# コードアップデート: bash deployment/deploy.sh --update
# ヘルプ: bash deployment/deploy.sh --help
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
set -euo pipefail

# ── 設定 ────────────────────────────────────────────────────────
APP_DIR="${APP_DIR:-/root/prompt-guild}"
SERVICE_NAME="prompt-guild"
BRANCH="${BRANCH:-main}"
REPO_URL="${REPO_URL:-}"  # 未設定の場合は git pull のみ

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; exit 1; }

# ── ヘルプ ───────────────────────────────────────────────────────
usage() {
    cat <<EOF
使い方:
  bash deployment/deploy.sh [オプション]

オプション:
  --setup    初回セットアップ (パッケージインストール・サービス登録・nginx 設定)
  --update   コードアップデートのみ (git pull → pip install → 再起動)
  --help     このヘルプを表示

環境変数:
  APP_DIR    インストール先 (デフォルト: /root/prompt-guild)
  BRANCH     デプロイするブランチ (デフォルト: main)
  REPO_URL   git clone する URL (--setup 時に必要)

例:
  REPO_URL=https://github.com/yourname/ai-content-frontend.git \\
    bash deployment/deploy.sh --setup

  bash deployment/deploy.sh --update
EOF
}

# ── 初回セットアップ ─────────────────────────────────────────────
cmd_setup() {
    info "=== 初回セットアップ開始 ==="

    # root チェック
    [[ $EUID -eq 0 ]] || error "setup は root で実行してください (sudo bash deployment/deploy.sh --setup)"

    # リポジトリ取得
    if [[ -d "$APP_DIR/.git" ]]; then
        warn "既存リポジトリを検出。git pull を実行します。"
        git -C "$APP_DIR" pull origin "$BRANCH"
    elif [[ -n "$REPO_URL" ]]; then
        info "リポジトリをクローン: $REPO_URL → $APP_DIR"
        git clone "$REPO_URL" "$APP_DIR"
        git -C "$APP_DIR" checkout "$BRANCH"
    else
        error "REPO_URL が未設定です。既存ディレクトリからセットアップする場合は --update を使用してください。"
    fi

    cd "$APP_DIR"

    # data/ ディレクトリ作成
    info "data/ ディレクトリを作成..."
    mkdir -p data

    # Python 依存インストール
    info "Python 依存パッケージをインストール..."
    pip install -r requirements.txt

    # .env ファイル作成
    if [[ ! -f ".env" ]]; then
        cp .env.example .env
        warn ".env ファイルを作成しました。必ず以下を編集してください:"
        warn "  JWT_SECRET   : openssl rand -hex 32 で生成したランダム値"
        warn "  COOKIE_SECURE: HTTPS 環境なら true"
        warn "  ADMIN_BOOTSTRAP_ENABLED=true + ADMIN_BOOTSTRAP_PASSWORD=<強固なパスワード>"
        warn ""
        warn "  nano $APP_DIR/.env  で編集後、もう一度このスクリプトを実行してください。"
        read -p "今すぐ .env を編集しますか? [y/N]: " yn
        [[ "$yn" =~ ^[Yy]$ ]] && ${EDITOR:-nano} .env
    else
        info ".env ファイルは既に存在します。"
    fi

    # systemd サービス登録
    info "systemd サービスを登録..."
    # WorkingDirectory を実際のパスに更新
    sed "s|/root/prompt-guild|$APP_DIR|g" deployment/prompt-guild.service \
        > /etc/systemd/system/${SERVICE_NAME}.service
    systemctl daemon-reload
    systemctl enable "${SERVICE_NAME}"
    systemctl restart "${SERVICE_NAME}"
    sleep 2
    systemctl is-active --quiet "${SERVICE_NAME}" \
        && info "サービス起動確認: OK" \
        || warn "サービスが起動していません。journalctl -u ${SERVICE_NAME} -n 30 で確認してください。"

    # nginx 確認
    if command -v nginx &>/dev/null; then
        info "nginx を検出しました。"
        NGINX_CONF="/etc/nginx/sites-available/${SERVICE_NAME}"
        if [[ ! -f "$NGINX_CONF" ]]; then
            warn "nginx 設定をコピーします (ドメイン名は後で変更してください):"
            warn "  sed -i 's/example.com/your-domain.com/g' $NGINX_CONF"
            cp deployment/nginx.conf "$NGINX_CONF"
            ln -sf "$NGINX_CONF" "/etc/nginx/sites-enabled/${SERVICE_NAME}"
            nginx -t && systemctl reload nginx \
                && info "nginx リロード完了" \
                || warn "nginx 設定にエラーがあります。nginx -t で確認してください。"
        else
            info "nginx 設定は既に存在します: $NGINX_CONF"
        fi
    else
        warn "nginx が見つかりません。手動で設定してください: deployment/nginx.conf"
    fi

    info ""
    info "=== セットアップ完了 ==="
    info "次のステップ:"
    info "  1. nano $APP_DIR/.env  で設定を確認"
    info "  2. journalctl -u ${SERVICE_NAME} -f  でログを確認"
    info "  3. ブラウザで http://<VPS-IP>/ にアクセスして動作確認"
    info ""
    info "管理者アカウント作成: .env の ADMIN_BOOTSTRAP_ENABLED=true に変更後"
    info "  systemctl restart ${SERVICE_NAME}"
}

# ── アップデート ─────────────────────────────────────────────────
cmd_update() {
    info "=== コードアップデート開始 ==="

    [[ -d "$APP_DIR/.git" ]] || error "リポジトリが見つかりません: $APP_DIR"
    cd "$APP_DIR"

    info "git pull (branch: $BRANCH)..."
    git pull origin "$BRANCH"

    info "pip install (差分のみ)..."
    pip install -r requirements.txt

    info "サービスを再起動..."
    systemctl restart "${SERVICE_NAME}"
    sleep 2
    systemctl is-active --quiet "${SERVICE_NAME}" \
        && info "再起動確認: OK" \
        || error "再起動に失敗しました。journalctl -u ${SERVICE_NAME} -n 50 で確認してください。"

    info "=== アップデート完了 ==="
}

# ── メイン ───────────────────────────────────────────────────────
case "${1:-}" in
    --setup)  cmd_setup ;;
    --update) cmd_update ;;
    --help|-h) usage ;;
    *) usage; exit 1 ;;
esac
