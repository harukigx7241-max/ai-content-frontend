# VPS デプロイ手順

## 前提環境

| 項目 | 要件 |
|------|------|
| OS | Ubuntu 22.04 / Debian 12 相当 |
| Python | 3.11 以上 |
| nginx | 1.18 以上 |
| VPS デフォルトパス | `/root/prompt-guild` |
| 最低スペック | 1 vCPU / 1 GB RAM / 20 GB SSD |

---

## 方法 A: deploy.sh を使う (推奨)

### 初回セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/<org>/ai-content-frontend.git /root/prompt-guild
cd /root/prompt-guild

# セットアップ実行 (root 必須)
bash deployment/deploy.sh --setup
```

スクリプトが以下を自動実行します:
1. `pip install -r requirements.txt`
2. `.env` ファイルを `.env.example` からコピー (なければ)
3. systemd サービス登録 + 起動
4. nginx 設定コピー + リロード

### コードアップデート

```bash
cd /root/prompt-guild
bash deployment/deploy.sh --update
```

---

## 方法 B: 手動手順

### 1. リポジトリ配置

```bash
cd /root
git clone https://github.com/<org>/ai-content-frontend.git prompt-guild
cd prompt-guild
mkdir -p data
pip install -r requirements.txt
```

### 2. 環境変数ファイルを作成

```bash
cp .env.example .env
nano .env
```

**最低限変更すべき項目:**

| 変数 | 変更内容 |
|------|---------|
| `JWT_SECRET` | `openssl rand -hex 32` で生成したランダム値 |
| `COOKIE_SECURE` | HTTPS 環境なら `true` |
| `ADMIN_BOOTSTRAP_ENABLED` | `true` に変更 (初回のみ) |
| `ADMIN_BOOTSTRAP_PASSWORD` | 推測困難なパスワード |

### 3. systemd サービス登録

```bash
cp deployment/prompt-guild.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable prompt-guild
systemctl start prompt-guild
systemctl status prompt-guild
```

ログ確認:
```bash
journalctl -u prompt-guild -f
```

### 4. nginx 設定

```bash
# ドメイン名を実際のものに置き換える
sed -i 's/example.com/your-domain.com/g' deployment/nginx.conf

cp deployment/nginx.conf /etc/nginx/sites-available/prompt-guild
ln -s /etc/nginx/sites-available/prompt-guild /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

#### HTTP のみで起動する場合 (IP 直打ち・SSL なし)

`deployment/nginx.conf` の HTTPS ブロックを削除し、以下の最小構成を使う:

```nginx
server {
    listen 80;
    server_name _;

    location /static/ {
        alias /root/prompt-guild/static/;
        expires 7d;
    }

    location / {
        proxy_pass       http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 5. 初回管理者アカウント作成

### 手順

```bash
# 1. .env を編集
nano /root/prompt-guild/.env
```

以下を設定:
```
ADMIN_BOOTSTRAP_ENABLED=true
ADMIN_BOOTSTRAP_PASSWORD=<推測困難なパスワード>  # admin123 は絶対に使わない
```

```bash
# 2. サービス再起動
systemctl restart prompt-guild

# 3. ログで確認 (WARNING が出れば作成成功)
journalctl -u prompt-guild -n 20 | grep -i bootstrap
```

### ログイン後の必須作業

1. `http://your-domain.com/login` にアクセス
2. `admin` / 設定したパスワードでログイン
3. マイページのオレンジ色の警告バナー → 「パスワードを変更 →」
4. 新しいパスワードに変更 (バナーが消えれば完了)
5. `.env` の `ADMIN_BOOTSTRAP_ENABLED=false` に変更
6. `systemctl restart prompt-guild`

### HQ (管理本部) アカウントの作成

```bash
# DB に直接ロールを設定する (SQLite の場合)
sqlite3 /root/prompt-guild/data/pguild.db \
  "UPDATE users SET role='headquarters' WHERE sns_handle='your_handle';"
systemctl restart prompt-guild
```

---

## 6. SSL 証明書 (Let's Encrypt)

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your-domain.com -d www.your-domain.com

# 自動更新確認
systemctl status certbot.timer
```

`deployment/nginx.conf` の `COOKIE_SECURE=false` → `true` に変更:
```bash
sed -i 's/COOKIE_SECURE=false/COOKIE_SECURE=true/' /root/prompt-guild/.env
systemctl restart prompt-guild
```

---

## 7. アップデート手順

```bash
cd /root/prompt-guild
bash deployment/deploy.sh --update
# または手動:
# git pull origin main
# pip install -r requirements.txt
# systemctl restart prompt-guild
```

---

## 8. 運用コマンド集

```bash
# サービス状態確認
systemctl status prompt-guild

# ログ表示 (リアルタイム)
journalctl -u prompt-guild -f

# ログ表示 (最新50行)
journalctl -u prompt-guild -n 50

# 再起動
systemctl restart prompt-guild

# メンテナンスモード ON (即時)
# /admin → システム設定 → メンテナンスモード または:
sed -i 's/ENABLE_MAINTENANCE_MODE=false/ENABLE_MAINTENANCE_MODE=true/' .env
systemctl restart prompt-guild

# メンテナンスモード OFF
sed -i 's/ENABLE_MAINTENANCE_MODE=true/ENABLE_MAINTENANCE_MODE=false/' .env
systemctl restart prompt-guild

# DB バックアップ (SQLite)
cp data/pguild.db data/pguild.db.bak.$(date +%Y%m%d_%H%M%S)
```

---

## 9. 環境変数チートシート

`/root/prompt-guild/.env` で設定する主要変数:

| 変数 | デフォルト | 説明 |
|------|----------|------|
| `JWT_SECRET` | (要変更) | JWT 署名鍵 |
| `DATABASE_URL` | `sqlite:///./data/pguild.db` | DB URL |
| `COOKIE_SECURE` | `false` | HTTPS 環境では `true` |
| `ENABLE_MAINTENANCE_MODE` | `false` | メンテナンスモード |
| `ENABLE_NOTICE_BANNER` | `false` | 告知バー表示 |
| `NOTICE_BANNER_TEXT` | `` | 告知バーのテキスト |
| `OPENAI_API_KEY` | `` | OpenAI API キー (任意) |
| `ANTHROPIC_API_KEY` | `` | Anthropic API キー (任意) |
| `LLM_PROVIDER` | `auto` | 優先 LLM プロバイダー |
| `API_MONTHLY_COST_LIMIT_USD` | `0` | 月次コスト上限 (0=無制限) |
| `ENABLE_BILLING` | `false` | Stripe 課金機能 |

全変数の説明: `.env.example` を参照。

---

## 10. トラブルシューティング

### サービスが起動しない

```bash
journalctl -u prompt-guild -n 100
```

よくある原因:
- `.env` が存在しない → `cp .env.example .env` して編集
- `data/` ディレクトリがない → `mkdir -p /root/prompt-guild/data`
- ポート 8000 が既に使用中 → `lsof -i :8000` で確認

### nginx 502 Bad Gateway

```bash
systemctl status prompt-guild   # アプリが起動しているか確認
curl http://127.0.0.1:8000/health  # 直接アクセスできるか確認
```

### DB 破損 (SQLite)

```bash
sqlite3 data/pguild.db "PRAGMA integrity_check;"
# 問題があればバックアップから復元:
cp data/pguild.db.bak.YYYYMMDD_HHMMSS data/pguild.db
systemctl restart prompt-guild
```
