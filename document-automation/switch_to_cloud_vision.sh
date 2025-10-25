#!/bin/bash

# Google Cloud Vision APIへの切り替えスクリプト

echo "========================================="
echo "Google Cloud Vision API への切り替え"
echo "========================================="

# 現在のディレクトリを確認
if [ ! -f "docker-compose.yml" ]; then
    echo "エラー: document-automationディレクトリで実行してください"
    exit 1
fi

# .envファイルのバックアップ
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
echo "✓ .envファイルをバックアップしました"

# OCR_ENGINEをcloudに変更
sed -i 's/^OCR_ENGINE=.*/OCR_ENGINE=cloud        # cloud (Google Vision), local (Tesseract)/' .env
echo "✓ OCR_ENGINE=cloud に変更しました"

# google-credentials.jsonの存在確認
if [ -f "config/google-credentials.json" ]; then
    echo "✓ google-credentials.json が見つかりました"
else
    echo "⚠ 警告: config/google-credentials.json が見つかりません"
    echo ""
    echo "以下の手順で認証情報ファイルを配置してください:"
    echo "1. Google Cloud Consoleでサービスアカウントキー(JSON)をダウンロード"
    echo "2. ファイル名を google-credentials.json にリネーム"
    echo "3. ~/nas-project/document-automation/config/ に配置"
    echo ""
    echo "その後、再度このスクリプトを実行してください"
    exit 1
fi

# プロジェクトIDの確認
CURRENT_PROJECT_ID=$(grep "^GOOGLE_CLOUD_PROJECT_ID=" .env | cut -d'=' -f2)
if [ "$CURRENT_PROJECT_ID" = "your-project-id" ]; then
    echo ""
    read -p "Google Cloud Project IDを入力してください: " PROJECT_ID
    sed -i "s/^GOOGLE_CLOUD_PROJECT_ID=.*/GOOGLE_CLOUD_PROJECT_ID=$PROJECT_ID/" .env
    echo "✓ プロジェクトIDを設定しました: $PROJECT_ID"
else
    echo "✓ プロジェクトID: $CURRENT_PROJECT_ID"
fi

# docker-compose.ymlを確認してconfig volumeマウントがあるか確認
if grep -q "./config:/app/config" docker-compose.yml; then
    echo "⚠ 警告: docker-compose.ymlにconfig volumeマウントがあります"
    echo "これは削除する必要があります（権限エラーの原因）"
    echo ""
    read -p "自動で削除しますか？ (y/n): " REMOVE_CONFIG
    if [ "$REMOVE_CONFIG" = "y" ]; then
        # configボリュームマウントを削除
        sed -i '/- \.\/config:\/app\/config/d' docker-compose.yml
        echo "✓ config volumeマウントを削除しました"
    fi
fi

echo ""
echo "========================================="
echo "設定完了！サービスを再起動します"
echo "========================================="

# webとworkerを再ビルド&再起動
sudo docker compose build --no-cache web worker
sudo docker compose restart web worker

echo ""
echo "✓ Google Cloud Vision APIへの切り替えが完了しました！"
echo ""
echo "次の手順:"
echo "1. ブラウザで http://$(hostname -I | awk '{print $1}'):8080 にアクセス"
echo "2. 新しいPDFファイルをアップロード"
echo "3. OCRエンジンが 'cloud' になっていることを確認"
echo ""
echo "ログ確認: sudo docker compose logs -f worker"
echo ""

