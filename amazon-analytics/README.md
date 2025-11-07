# Amazon Purchase Analytics System

Amazon購入履歴を分析し、支出パターンの可視化、無駄遣い検出、購買傾向分析を行うシステムです。

## 📋 機能

### ✅ 実装済み

1. **CSV取り込み機能**
   - Amazon注文履歴CSVの自動解析
   - ドラッグ&ドロップアップロード
   - 重複データの自動除外

2. **データ分析**
   - カテゴリ別支出集計
   - 購入履歴の可視化
   - 統計情報の表示

3. **AI分析機能**
   - OpenAI APIによる自動カテゴリ分類
   - 衝動買いパターン検出
   - 定期購入候補の提案
   - 月次インサイト生成

4. **ダッシュボード**
   - リアルタイム統計表示
   - カテゴリ別支出グラフ
   - 購入履歴一覧
   - インポート履歴

## 🚀 クイックスタート

### 前提条件

- Docker & Docker Compose
- OpenAI APIキー（AI機能を使用する場合）

### インストール

1. リポジトリをクローン
```bash
cd /Users/Yoshi/nas-project/amazon-analytics
```

2. 環境変数を設定
```bash
cp env.example .env
# .envファイルを編集してAPIキーやパスワードを設定
```

3. Docker Composeで起動
```bash
docker-compose up -d  # .envを使用します
```

4. ブラウザでアクセス
```
http://localhost:8000
```

## 📊 使い方

### 1. AmazonからCSVをダウンロード

1. Amazonにログイン
2. アカウント → 注文履歴 → 注文データをダウンロード
3. `Retail.OrderHistory.3.csv` をダウンロード

### 2. CSVをアップロード

1. ダッシュボードの「アップロード」タブ
2. CSVファイルをドラッグ&ドロップ
3. 自動的にデータが取り込まれます

### 3. データを分析

- **概要タブ**: 総支出額、カテゴリ別グラフを確認
- **購入履歴タブ**: 詳細な購入リストを表示
- **分析タブ**: AI分析を実行
  - 自動カテゴリ分類
  - 衝動買い検出
  - 定期購入候補
  - 月次インサイト

## 🗂️ プロジェクト構造

```
amazon-analytics/
├── app/
│   ├── api/              # FastAPI エンドポイント
│   │   ├── main.py       # メインアプリケーション
│   │   └── routes.py     # APIルート
│   ├── models/           # データベースモデル
│   │   ├── database.py   # DB設定
│   │   └── purchase.py   # Purchase/Category/etc.
│   ├── services/         # ビジネスロジック
│   │   ├── csv_parser.py      # CSV解析
│   │   ├── data_processor.py  # データ処理
│   │   └── ai_analyzer.py     # AI分析
│   ├── static/           # 静的ファイル
│   │   ├── css/
│   │   └── js/
│   └── templates/        # HTMLテンプレート
├── config/               # 設定ファイル
├── data/                 # データディレクトリ
├── docker-compose.yml    # Docker構成
└── requirements.txt      # Python依存関係
```

## 🔧 設定

### データベース

PostgreSQLを使用しています。接続情報は`.env`で設定します。

```env
DATABASE_URL=postgresql://postgres:password@db:5432/amazon_analytics
```

### OpenAI API

AI機能を使用するには、OpenAI APIキーが必要です。

```env
OPENAI_API_KEY=sk-your-api-key-here
```

## 📊 データベーススキーマ

### purchases（購入履歴）
- 注文情報（order_id, order_date）
- 商品情報（product_name, asin）
- 価格情報（unit_price, total_owed）
- カテゴリ（AI分類結果）

### categories（カテゴリマスタ）
- デフォルトカテゴリ
  - 食品・飲料
  - 日用品・消耗品
  - 家電・PC関連
  - 本・メディア
  - ファッション
  - ホビー・趣味
  - 健康・美容
  - ペット用品
  - その他

### analysis_results（分析結果）
- 分析タイプ（月次、年次、パターン等）
- 対象期間
- 結果データ（JSON）

### import_history（取り込み履歴）
- ファイル名
- 取り込み日時
- レコード数
- ステータス

## 🛠️ 開発

### ローカル開発

```bash
# 仮想環境作成
python -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt

# データベース起動（Docker）
docker-compose up -d db redis  # .envを使用します

# 開発サーバー起動
uvicorn app.api.main:app --reload
```

### テスト

```bash
# 仮想環境に入る
source venv/bin/activate

# CSVパーサーのテスト
python -c "from app.services.csv_parser import csv_parser; print(csv_parser)"
```

## 📝 API エンドポイント

- `GET /` - ダッシュボード
- `GET /api/health` - ヘルスチェック
- `POST /api/upload` - CSVアップロード
- `GET /api/statistics` - 統計情報
- `GET /api/purchases` - 購入履歴取得
- `POST /api/analyze/classify` - 自動分類
- `GET /api/analyze/impulse` - 衝動買い分析
- `GET /api/analyze/recurring` - 定期購入分析
- `GET /api/analyze/monthly-insights` - 月次インサイト

## 🔮 今後の拡張予定

- [ ] レポート生成機能（PDF出力）
- [ ] Notion連携（レポート自動投稿）
- [ ] メール通知（月次レポート）
- [ ] 予算管理機能
- [ ] グラフの種類追加
- [ ] 楽天市場対応
- [ ] 音声問い合わせ対応

## 📄 ライセンス

MIT License

## 👤 作成者

Yoshi - 2025年10月

