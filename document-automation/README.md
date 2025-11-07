# ドキュメント自動処理システム (Document Automation System) v1.0.0

PDF・画像ファイルをアップロードするだけで、OCR処理、AI要約、自動カテゴリ分類を行い、効率的なドキュメント管理を実現するシステムです。

## 📌 バージョン情報

- **バージョン**: v1.0.0
- **リリース名**: 初期リリース版
- **リリース日**: 2025-10-19

## 🚀 主要機能

### v1.0.0 実装済み機能
- ✅ **ファイルアップロード**: PDF、JPEG、PNG対応（最大50MB）
- ✅ **ドラッグ&ドロップUI**: 直感的なファイルアップロード
- ✅ **高精度OCR処理**: Google Cloud Vision API による高精度テキスト抽出
- ✅ **AI要約・分類**: Gemini 2.5 Flash による高精度分析
- ✅ **動的カテゴリ生成**: 13種類の固定カテゴリ + 柔軟な自動生成
- ✅ **個別マークダウンエクスポート**: ZIP形式で一括ダウンロード
- ✅ **元ファイル一括ダウンロード**: ZIP形式で一括ダウンロード
- ✅ **AI統合要約**: 複数文書の統合分析レポート生成
- ✅ **日本語対応UI**: 完全日本語インターフェース
- ✅ **バージョン管理**: システムバージョン表示・管理

### 今後の拡張（v1.1.0以降）
- 🔜 Notion連携
- 🔜 Google Drive連携
- 🔜 高度な検索・フィルタ
- 🔜 メール通知
- 🔜 バッチ処理の改善

## 📊 システム構成

### ハイブリッドアーキテクチャ

```
┌─────────────────┐
│   Web UI        │ ← ユーザーインターフェース
│   (FastAPI)     │
└────────┬────────┘
         │
         ├─ Local Processing (NAS)
         │  ├─ ファイル管理
         │  ├─ データベース (PostgreSQL)
         │  └─ タスクキュー (Redis + Celery)
         │
         └─ Cloud Processing (外部API)
            ├─ OCR: Google Cloud Vision API
            └─ AI要約: Gemini 2.5 Flash
```

**メリット:**
- 💰 **低コスト**: 月額$3-10程度（100-300ページ処理）
- 🚀 **高速・高精度**: クラウドAIの性能活用
- 🔋 **NAS負荷最小**: メモリ8GBでも快適動作
- 📈 **スケーラブル**: 処理量に応じて柔軟に対応

## 🛠️ 技術スタック

### バックエンド
- **言語**: Python 3.11+
- **Webフレームワーク**: FastAPI
- **非同期処理**: Celery + Redis
- **データベース**: PostgreSQL

### 外部API
- **OCR**: Google Cloud Vision API
- **AI要約・分類**: Google Gemini 2.5 Flash
- **フォールバック**: Tesseract OCR（ローカル）

### フロントエンド
- **フレームワーク**: Bootstrap 5
- **JavaScript**: Vanilla JS (依存なし)

### インフラ
- **コンテナ**: Docker + Docker Compose
- **NAS**: UGREEN DXP2800 (Intel N100, 8GB RAM)

## 📦 デプロイ

### 前提条件

1. **ハードウェア**
   - UGREEN DXP2800（または同等のNAS）
   - メモリ: 8GB以上推奨
   - ストレージ: 512GB SSD（キャッシュ用）推奨

2. **ソフトウェア**
   - Docker & Docker Compose
   - SSH アクセス

3. **API キー**（無料枠で開始可能）
   - Google Gemini API キー: https://makersuite.google.com/app/apikey
   - Google Cloud プロジェクト（Vision API用、オプション）

### クイックスタート

#### 1. プロジェクトのクローン

```bash
# NASに接続
ssh -p 23456 YOUR_USERNAME@YOUR_IP_ADDRESS110

# プロジェクトディレクトリに移動
cd ~/nas-project/document-automation
```

#### 2. 環境変数の設定

```bash
# env.exampleをコピー
cp env.example .env

# 環境変数を編集
nano .env
```

**.env の必須設定:**

```bash
# Gemini API キー（必須）
GEMINI_API_KEY=your-gemini-api-key-here

# Google Cloud（オプション：高精度OCR使用時）
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/app/config/google-credentials.json

# 処理モード
PROCESSING_MODE=hybrid  # hybrid, cloud, local
OCR_ENGINE=cloud        # cloud または local（Geminiのみの場合はlocal）
```

#### 3. データディレクトリの作成

```bash
# NAS上にデータディレクトリを作成
sudo mkdir -p /volume2/data/doc-automation/{uploads,processed,exports,cache,db}
sudo chown -R YOUR_USERNAME:users /volume2/data/doc-automation
```

#### 4. Docker Composeでデプロイ

```bash
# コンテナをビルド・起動
sudo docker compose up -d

# ログ確認
sudo docker compose logs -f
```

#### 5. アクセス

- **Web UI**: http://YOUR_IP_ADDRESS110:8080
- **API ドキュメント**: http://YOUR_IP_ADDRESS110:8080/docs
- **ヘルスチェック**: http://YOUR_IP_ADDRESS110:8080/health

## 🎯 使い方

### 基本的なワークフロー

1. **ファイルアップロード**
   - Web UIからPDF・画像をアップロード
   - 複数ファイルの一括アップロード可能

2. **自動処理**
   - OCR処理（クラウドまたはローカル）
   - AI要約・カテゴリ分類
   - メタデータ抽出

3. **結果確認**
   - ドキュメント一覧で状態確認
   - 詳細ビューで要約・キーワード確認

4. **エクスポート**
   - 個別マークダウンエクスポート
   - 複数文書の一括エクスポート
   - 統合要約の生成

### API使用例

#### ファイルアップロード

```bash
curl -X POST "http://YOUR_IP_ADDRESS110:8080/api/upload" \
  -F "file=@document.pdf"
```

#### ドキュメント一覧取得

```bash
curl "http://YOUR_IP_ADDRESS110:8080/api/documents?status=completed&limit=10"
```

#### マークダウンエクスポート

```bash
curl "http://YOUR_IP_ADDRESS110:8080/api/export/1/markdown" \
  -o document.md
```

## 💰 コスト試算

### Google Gemini API（必須）

| 使用量/月 | コスト/月 | 備考 |
|----------|----------|------|
| 50ページ | $0.30 | ☕ コーヒー1杯以下 |
| 200ページ | $1.10 | 🍔 ランチ1食以下 |
| 500ページ | $2.75 | 🍜 ラーメン1杯程度 |
| 2000ページ | $11.00 | 🎬 映画1回分 |

### Google Cloud Vision API（オプション）

| 使用量/月 | コスト/月 | 備考 |
|----------|----------|------|
| 0-1000ページ | 無料 | 無料枠内 |
| 1001-5000ページ | $1.50/千ページ | 高精度OCR |

**合計コスト（想定）**: 月額$3-10程度

## 🔧 設定

### 処理モードの選択

**.env で設定:**

```bash
# コストバランス型（推奨）
PROCESSING_MODE=hybrid
COST_MODE=balanced
OCR_ENGINE=cloud
AI_PROVIDER=gemini

# コスト重視型
PROCESSING_MODE=local
COST_MODE=save
OCR_ENGINE=local
AI_PROVIDER=gemini  # 要約のみクラウド

# 性能重視型
PROCESSING_MODE=cloud
COST_MODE=performance
OCR_ENGINE=cloud
AI_PROVIDER=gemini
```

### カテゴリ設定

自動分類されるカテゴリ:
- 請求書・領収書
- 契約書・同意書
- 見積書・提案書
- 会議資料・報告書
- プレゼンテーション資料
- 医療・健康記録
- 税務・確定申告関連
- 保険関連
- 公的書類
- メモ・手書きノート
- 名刺
- レシート
- その他

## 🐳 Docker コマンド

### 基本操作

```bash
# コンテナ起動
sudo docker compose up -d

# コンテナ停止
sudo docker compose down

# ログ確認
sudo docker compose logs -f web
sudo docker compose logs -f worker

# コンテナ再起動
sudo docker compose restart

# コンテナ状態確認
sudo docker compose ps
```

### デバッグ

```bash
# コンテナ内でコマンド実行
sudo docker exec -it doc-automation-web bash

# データベース接続
sudo docker exec -it doc-automation-db psql -U docuser -d document_automation

# Redis確認
sudo docker exec -it doc-automation-redis redis-cli
```

## 📊 監視とメンテナンス

### ヘルスチェック

```bash
# システム状態確認
curl http://YOUR_IP_ADDRESS110:8080/health

# 統計情報確認
curl http://YOUR_IP_ADDRESS110:8080/api/stats
```

### ログ確認

```bash
# エラーログのみ表示
sudo docker compose logs | grep -i error | tail -20

# 特定サービスのログ
sudo docker compose logs worker --tail=50
```

### データバックアップ

```bash
# データベースバックアップ
sudo docker exec doc-automation-db pg_dump -U docuser document_automation > backup_$(date +%Y%m%d).sql

# ファイルバックアップ
sudo tar -czf doc_automation_backup_$(date +%Y%m%d).tar.gz /volume2/data/doc-automation/
```

## 🔒 セキュリティ

### 推奨設定

1. **APIキーの保護**
   ```bash
   chmod 600 .env
   ```

2. **ネットワーク制限**
   - 内部ネットワークのみアクセス許可
   - 外部公開時はVPN/Cloudflare Tunnel使用

3. **定期更新**
   ```bash
   # イメージ更新
   sudo docker compose pull
   sudo docker compose up -d
   ```

## 🐛 トラブルシューティング

### よくある問題

#### 1. コンテナが起動しない

```bash
# ログ確認
sudo docker compose logs

# ポート競合確認
sudo netstat -tlnp | grep 8080
```

#### 2. OCR処理が失敗する

- Tesseractの日本語データ確認:
  ```bash
  sudo docker exec doc-automation-worker tesseract --list-langs
  ```

#### 3. Gemini APIエラー

- APIキーの確認:
  ```bash
  sudo docker exec doc-automation-web env | grep GEMINI
  ```

- API制限確認: https://makersuite.google.com/

#### 4. データベース接続エラー

```bash
# データベース再起動
sudo docker compose restart db

# 接続テスト
sudo docker exec doc-automation-web python -c "from app.models.database import engine; print(engine.connect())"
```

## 📈 パフォーマンス最適化

### NAS設定

1. **512GB SSDをキャッシュに設定**
   - UGOS Proの設定でキャッシュドライブとして指定

2. **Docker データディレクトリをSSDに配置**
   ```bash
   # docker-compose.ymlのvolumesをSSD配下に変更
   ```

### 処理速度

| ドキュメントタイプ | 平均処理時間 | 備考 |
|-----------------|------------|------|
| 1ページPDF | 10-15秒 | クラウドOCR |
| 10ページPDF | 1-2分 | 並列処理 |
| 画像ファイル | 5-10秒 | 高速処理 |

## 🚀 今後の拡張

### Phase 2（予定）
- [ ] Notion API連携
- [ ] Google Drive連携
- [ ] メール通知機能
- [ ] 高度な検索・フィルタ

### Phase 3（予定）
- [ ] 表データの自動スプレッドシート化
- [ ] 手書き文字認識の精度向上
- [ ] 多言語翻訳機能
- [ ] Slack/Teams連携

## 📞 サポート

問題が発生した場合:

1. [トラブルシューティング](#🐛-トラブルシューティング)を確認
2. ログファイルを確認
3. GitHub Issuesで報告

## 📄 ライセンス

MIT License

---

**最終更新**: 2025年10月18日  
**バージョン**: 1.0.0 (MVP)  
**作成者**: AI Assistant

## 🎉 開発完了！

ドキュメント自動処理システムのMVP版が完成しました！

次のステップ:
1. Google Gemini APIキーを取得
2. `.env`ファイルを設定
3. `docker compose up -d`でデプロイ
4. Web UIからファイルをアップロード

Happy Documenting! 📄✨

