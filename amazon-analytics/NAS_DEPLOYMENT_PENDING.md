# NASデプロイ保留中

## 📅 ステータス

**現在の状態**: ローカル開発完了、NASデプロイ保留中  
**停止日**: 2025年10月21日  
**バージョン**: 1.0.0 (Build 1)

---

## ✅ ローカルで完了した内容

### 1. 機能実装
- ✅ CSV取り込み機能（Amazon Retail.OrderHistory.3.csv対応）
- ✅ Gemini AI自動カテゴリ分類（レート制限対応済み）
- ✅ 購買パターン分析（衝動買い検出、定期購入候補）
- ✅ 月次インサイト生成
- ✅ Webダッシュボード（Chart.js統合）
- ✅ レポート生成（月次/年次/グラフ/CSV出力）

### 2. インフラ
- ✅ Docker Compose構成
- ✅ PostgreSQL + Redis
- ✅ Apple Silicon Docker Desktop対応
- ✅ 環境変数管理（.env）

### 3. 動作確認
- ✅ 1,270件のデータ取り込み成功
- ✅ 22年分の購入履歴（2003-2025）
- ✅ 総支出額: ¥4,160,851
- ✅ すべてのAPI動作確認完了

---

## 🔄 ローカルでの再起動方法

```bash
cd /Users/Yoshi/nas-project/amazon-analytics

# 起動
docker-compose --env-file .env up -d

# 停止
docker-compose --env-file .env down

# ログ確認
docker-compose logs -f web

# ブラウザでアクセス
open http://localhost:8000
```

---

## 📦 NASデプロイ時の準備事項

### 1. 環境設定ファイルの配置

NAS上に`.env`を配置：
```bash
# NASの適切な場所にコピー
scp .env user@nas:/volume2/docker/amazon-analytics/.env
```

### 2. docker-compose.yml の修正

ボリュームパスをNAS用に変更：
```yaml
volumes:
  - /volume2/data/amazon-analytics/uploads:/app/data/uploads
  - /volume2/data/amazon-analytics/processed:/app/data/processed
  - /volume2/data/amazon-analytics/exports:/app/data/exports
  - /volume2/data/amazon-analytics/cache:/app/data/cache
```

### 3. ポート設定

他のサービスと衝突しないポートを設定：
```yaml
ports:
  - "8001:8000"  # 例: 8001番ポートに変更
```

### 4. データベースパスワード

NAS用に独自のパスワードを設定：
```env
POSTGRES_PASSWORD=nas_amazon_analytics_secure_password
```

---

## 🗂️ プロジェクト構造

```
amazon-analytics/
├── .env              ← 実際のAPIキー（git管理外）
├── env.example             ← テンプレート
├── docker-compose.yml      ← Docker構成
├── Dockerfile              ← コンテナ定義
├── deploy.sh               ← デプロイスクリプト
├── setup.sh                ← セットアップスクリプト
├── app/
│   ├── api/                ← FastAPI
│   ├── models/             ← データベースモデル
│   ├── services/           ← ビジネスロジック
│   ├── static/             ← CSS/JS
│   └── templates/          ← HTML
├── config/
│   ├── settings.py         ← 設定管理
│   └── version.py          ← バージョン管理
├── data/                   ← データディレクトリ
│   ├── uploads/
│   ├── processed/
│   ├── exports/
│   └── cache/
└── [ドキュメント]
    ├── README.md
    ├── QUICKSTART.md
    ├── SETUP_GUIDE.md
    ├── PROJECT_SUMMARY.md
    └── DEPLOYMENT_SUCCESS.md
```

---

## 🔧 使用技術

### バックエンド
- Python 3.11
- FastAPI 0.115.0
- SQLAlchemy 2.0
- Pandas 2.2
- Gemini API (google-generativeai 0.8.3)

### データベース
- PostgreSQL 15
- Redis 7

### フロントエンド
- Vanilla JavaScript
- Chart.js 4.4
- CSS3

---

## 📊 データ構造

### PostgreSQLテーブル
1. **purchases** - 購入履歴（1,270件取り込み済み）
2. **categories** - カテゴリマスタ（9カテゴリ）
3. **analysis_results** - 分析結果
4. **import_history** - 取り込み履歴

---

## ⚠️ 注意事項

### Gemini APIレート制限
- **15リクエスト/分**
- **1,500リクエスト/日**
- コードにレート制限対応済み（10件ごとに4秒待機）

### データベースボリューム
- 初回起動時はデータベース初期化に時間がかかります
- ボリュームを削除すると全データが消えます
  ```bash
  # 注意: データが消えます
  docker-compose down -v
  ```

---

## 🎯 NASデプロイ時の手順（参考）

### 1. プロジェクトをNASに転送
```bash
# プロジェクト全体をNASにコピー
rsync -av --exclude 'data/' --exclude '__pycache__' \
  /Users/Yoshi/nas-project/amazon-analytics/ \
  user@nas:/volume2/docker/amazon-analytics/
```

### 2. 環境変数を設定
```bash
# NAS上で.envを作成/編集
ssh user@nas
cd /volume2/docker/amazon-analytics
nano .env
```

### 3. docker-compose.ymlを修正
- ボリュームパスをNAS用に変更
- ポート番号を調整
- 必要に応じてメモリ制限を追加

### 4. 起動
```bash
# NAS上で
cd /volume2/docker/amazon-analytics
docker-compose --env-file .env up -d
```

---

## 📝 メモ

- ローカルでの動作確認完了
- Gemini API統合成功
- 22年分のデータ（1,270件）取り込み成功
- レート制限対応実装済み
- NASデプロイは必要に応じて実施

---

## 🔗 関連ドキュメント

- **QUICKSTART.md** - クイックスタート
- **SETUP_GUIDE.md** - 詳細セットアップ
- **PROJECT_SUMMARY.md** - 技術仕様
- **GEMINI_SETUP_COMPLETE.md** - Gemini API対応
- **DEPLOYMENT_SUCCESS.md** - デプロイ完了報告

---

**プロジェクトステータス**: ✅ ローカル開発完了  
**NASデプロイ**: ⏸️ 保留中  
**再開時**: このドキュメントを参照

