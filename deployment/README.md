# 本番デプロイ手順

## 前提

- OS: Ubuntu 22.04 / Debian 12 相当
- Python 3.11+
- nginx
- VPS のパス: `/root/prompt-guild`

---

## 1. リポジトリ配置

```bash
cd /root
git clone https://github.com/<org>/ai-content-frontend.git prompt-guild
cd prompt-guild
pip install -r requirements.txt
```

---

## 2. 環境変数ファイルを作成

```bash
cp .env.example .env
nano .env   # 必要な値を編集
```

**最低限変更すべき項目:**

| 変数 | 変更内容 |
|------|---------|
| `JWT_SECRET` | ランダムな長い文字列 (`openssl rand -hex 32`) |
| `COOKIE_SECURE` | HTTPS 環境なら `true` |
| `ADMIN_BOOTSTRAP_PASSWORD` | 推測困難なパスワードに変更 |

---

## 3. systemd サービス登録

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

---

## 4. nginx 設定

```bash
# ドメイン名を実際のものに置き換える
sed -i 's/example.com/your-domain.com/g' deployment/nginx.conf

cp deployment/nginx.conf /etc/nginx/sites-available/prompt-guild
ln -s /etc/nginx/sites-available/prompt-guild /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

### HTTP のみで起動する場合 (SSL なし)

`deployment/nginx.conf` の HTTPS ブロックを削除し、80番ポートで直接プロキシする:

```nginx
server {
    listen 80;
    server_name your-domain.com;

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

## 5. 初回管理者アカウント

**安全設計:**
- `.env.example` のデフォルトは `ADMIN_BOOTSTRAP_ENABLED=false`
- 既存の管理者が1件でもいれば、bootstrap は何もしない（べき等）
- bootstrap で作成された管理者は `must_change_password=true` フラグが付き、マイページに警告バナーが表示される

**手順:**

```bash
# 1. .env を編集して bootstrap を有効化 + 強固なパスワードを設定
nano .env
```

```
ADMIN_BOOTSTRAP_ENABLED=true
ADMIN_BOOTSTRAP_PASSWORD=<推測困難なパスワード>  # ← admin123 は絶対に使わない
```

```bash
# 2. サービスを起動 (または再起動) — 起動ログに WARNING が出れば成功
systemctl restart prompt-guild
journalctl -u prompt-guild -n 20 | grep bootstrap
```

**ログイン後の必須作業:**

1. `/login` で管理者アカウントにログイン
2. マイページのオレンジ色の警告バナー →「パスワードを変更 →」ボタン
3. 設定タブ → パスワード変更フォームで新しいパスワードに変更（変更後バナーが消える）
4. `.env` の `ADMIN_BOOTSTRAP_ENABLED=false` に変更（またはコメントアウト）
5. `systemctl restart prompt-guild`

---

## 6. アップデート手順

```bash
cd /root/prompt-guild
git pull origin main
pip install -r requirements.txt   # 依存関係が増えた場合
systemctl restart prompt-guild
```
