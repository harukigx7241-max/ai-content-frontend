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

`.env` で `ADMIN_BOOTSTRAP_ENABLED=true` のままサービスを起動すると、
起動時に管理者アカウントが自動作成されます。

**初回ログイン後の必須作業:**

1. `/login` で管理者アカウントにログイン
2. マイページ → 設定タブ → パスワード変更
3. `.env` の `ADMIN_BOOTSTRAP_ENABLED=false` に変更
4. `systemctl restart prompt-guild`

---

## 6. アップデート手順

```bash
cd /root/prompt-guild
git pull origin main
pip install -r requirements.txt   # 依存関係が増えた場合
systemctl restart prompt-guild
```
