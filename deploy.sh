#!/bin/bash
set -e
cd ~/ai-content-pro

# バージョン番号を引数で受け取る（例: ./deploy.sh 74.0.1）
VERSION=${1:-"$(date +%Y%m%d%H%M)"}

echo "🚀 デプロイ開始: v$VERSION"

# Gitコミット＆プッシュ
git add -A
git commit -m "deploy: v$VERSION" || echo "変更なし、スキップ"
git push origin main

# サービス再起動
sudo systemctl restart aicontent.service
sleep 2
sudo systemctl status aicontent.service --no-pager | head -5

echo "✅ デプロイ完了: v$VERSION"
