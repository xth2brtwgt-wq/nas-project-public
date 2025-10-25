# Amazon Purchase Analytics System - プロジェクトサマリー

## 📌 プロジェクト概要

**目的**: AmazonからダウンロードしたCSV購入履歴を自動取り込み・分析し、支出パターンの可視化、無駄遣い検出、購買傾向分析を行う

**開発期間**: 2025年10月  
**バージョン**: 1.0.0  
**ステータス**: ✅ Phase 1-3 実装完了

---

## ✅ 実装済み機能

### 1. データ取り込み機能
- ✅ CSV自動解析（Retail.OrderHistory.3.csv対応）
- ✅ ドラッグ&ドロップアップロード
- ✅ 重複データの自動除外
- ✅ データクレンジング
- ✅ インポート履歴管理

### 2. データベース設計
- ✅ PostgreSQL統合
- ✅ 購入履歴テーブル（purchases）
- ✅ カテゴリマスタ（categories）
- ✅ 分析結果保存（analysis_results）
- ✅ インポート履歴（import_history）

### 3. AI分析機能
- ✅ OpenAI APIによる自動カテゴリ分類
- ✅ 衝動買いパターン検出
- ✅ 定期購入候補の提案
- ✅ 月次インサイト生成（AIアドバイス）

### 4. ダッシュボードUI
- ✅ リアルタイム統計表示
- ✅ カテゴリ別支出円グラフ
- ✅ 購入履歴一覧
- ✅ フィルタ・検索機能
- ✅ レスポンシブデザイン

### 5. レポート生成
- ✅ 月次レポート生成
- ✅ 年次レポート生成
- ✅ カテゴリ別グラフ出力
- ✅ 月別推移グラフ
- ✅ CSV エクスポート

### 6. インフラ
- ✅ Docker Compose構成
- ✅ PostgreSQL + Redis
- ✅ FastAPI + Uvicorn
- ✅ 環境変数管理

---

## 🗂️ プロジェクト構造

```
amazon-analytics/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPIメインアプリ
│   │   ├── routes.py            # APIエンドポイント
│   │   └── report_routes.py    # レポート用API
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py          # DB接続・設定
│   │   └── purchase.py          # データモデル
│   ├── services/
│   │   ├── __init__.py
│   │   ├── csv_parser.py        # CSV解析
│   │   ├── data_processor.py   # データ処理
│   │   ├── ai_analyzer.py      # AI分析
│   │   └── report_generator.py # レポート生成
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css        # スタイルシート
│   │   └── js/
│   │       └── app.js           # フロントエンドJS
│   └── templates/
│       └── index.html           # ダッシュボードHTML
├── config/
│   ├── __init__.py
│   ├── settings.py              # 設定管理
│   └── version.py               # バージョン情報
├── data/                        # データディレクトリ
│   ├── uploads/                 # CSVアップロード先
│   ├── processed/               # 処理済みデータ
│   ├── exports/                 # エクスポート先
│   └── cache/                   # キャッシュ
├── utils/
│   └── __init__.py
├── docker-compose.yml           # Docker構成
├── Dockerfile                   # コンテナ定義
├── requirements.txt             # Python依存関係
├── env.example                  # 環境変数テンプレート
├── .gitignore
├── README.md                    # 基本ドキュメント
├── SETUP_GUIDE.md              # セットアップガイド
├── PROJECT_SUMMARY.md          # このファイル
└── test_setup.py               # セットアップテスト
```

---

## 🔧 技術スタック

### バックエンド
- **Python 3.11+**
- **FastAPI** - Webフレームワーク
- **Pandas** - データ処理
- **SQLAlchemy** - ORM
- **OpenAI API** - AI分析

### データベース
- **PostgreSQL 15** - メインDB
- **Redis 7** - キャッシュ

### フロントエンド
- **Vanilla JavaScript**
- **Chart.js** - グラフ描画
- **CSS3** - モダンUI

### インフラ
- **Docker & Docker Compose**
- **Uvicorn** - ASGIサーバー

### 可視化・分析
- **Matplotlib** - グラフ生成
- **Plotly** - インタラクティブグラフ

---

## 📊 データフロー

### 1. CSV取り込みフロー
```
ユーザー → CSV アップロード → FastAPI
  ↓
csv_parser (解析)
  ↓
data_processor (クレンジング・保存)
  ↓
PostgreSQL
```

### 2. AI分析フロー
```
データベース → ai_analyzer
  ↓
OpenAI API (分類・インサイト生成)
  ↓
分析結果保存 → ダッシュボード表示
```

### 3. レポート生成フロー
```
期間指定 → report_generator
  ↓
データ集計・グラフ生成
  ↓
PNG/CSV エクスポート
```

---

## 📈 実装された分析機能

### 1. カテゴリ別分析
- 9つのデフォルトカテゴリ
- AI自動分類
- カテゴリ別支出集計
- 円グラフ可視化

### 2. 時系列分析
- 月別支出推移
- 年次トレンド
- 前月比較
- 折れ線グラフ表示

### 3. パターン検出
- 衝動買いアラート（1週間に3回以上）
- 定期購入候補（3回以上の繰り返し）
- 購入間隔分析

### 4. AIインサイト
- 支出パターン分析
- 節約アドバイス生成
- カスタマイズ提案

---

## 🎯 要件達成状況

| 機能カテゴリ | 進捗 | 備考 |
|-------------|------|------|
| CSV取り込み | ✅ 100% | 自動解析・重複除外完了 |
| データベース設計 | ✅ 100% | 4テーブル実装完了 |
| AI分析 | ✅ 100% | OpenAI統合完了 |
| ダッシュボード | ✅ 100% | レスポンシブUI完成 |
| レポート生成 | ✅ 100% | 月次・年次・グラフ対応 |
| Docker化 | ✅ 100% | Compose構成完了 |
| 外部連携 | ⏸️ 未実装 | Notion/メール（Phase 4） |

---

## 📝 API エンドポイント一覧

### 基本
- `GET /` - ダッシュボード
- `GET /api/health` - ヘルスチェック

### データ管理
- `POST /api/upload` - CSVアップロード
- `GET /api/statistics` - 統計情報
- `GET /api/purchases` - 購入履歴取得
- `GET /api/categories` - カテゴリ一覧
- `GET /api/import-history` - インポート履歴

### AI分析
- `POST /api/analyze/classify` - 自動カテゴリ分類
- `GET /api/analyze/impulse` - 衝動買い検出
- `GET /api/analyze/recurring` - 定期購入分析
- `GET /api/analyze/monthly-insights` - 月次インサイト

### レポート
- `GET /api/report/monthly` - 月次レポート
- `GET /api/report/yearly` - 年次レポート
- `GET /api/report/chart/category` - カテゴリ円グラフ
- `GET /api/report/chart/trend` - 月別推移グラフ
- `GET /api/report/export/csv` - CSV エクスポート

---

## 🚀 デプロイ方法

### Docker Compose（推奨）

```bash
# 1. 環境設定
cp env.example .env
nano .env  # APIキー等を設定

# 2. 起動
docker-compose up -d

# 3. アクセス
# http://localhost:8000
```

### ローカル開発

```bash
# 1. 仮想環境
python -m venv venv
source venv/bin/activate

# 2. 依存関係
pip install -r requirements.txt

# 3. DB起動
docker-compose up -d db redis

# 4. アプリ起動
uvicorn app.api.main:app --reload
```

---

## 🔮 今後の拡張候補

### Phase 4: 外部連携（未実装）
- [ ] Notion APIレポート自動投稿
- [ ] メール通知（月次レポート）
- [ ] Google Sheets連携
- [ ] Slack通知

### Phase 5: 高度な機能
- [ ] 予算管理機能
- [ ] 価格変動追跡
- [ ] 類似商品検索
- [ ] 音声問い合わせ

### Phase 6: 拡張対応
- [ ] 楽天市場CSV対応
- [ ] Yahoo!ショッピング対応
- [ ] メール自動取り込み
- [ ] 家族アカウント統合

---

## 📊 パフォーマンス

### 処理性能
- CSV解析: 1万行 < 30秒
- ダッシュボード表示: < 3秒
- レポート生成: < 1分
- AI分類: 100商品 < 2分

### スケーラビリティ
- データ保持期間: 5年間
- 最大CSV サイズ: 10MB
- 同時接続: 20ユーザー（推奨）

---

## 🔐 セキュリティ対策

### 実装済み
- ✅ 環境変数での秘密情報管理
- ✅ PostgreSQL認証
- ✅ CSVファイル検証
- ✅ SQLインジェクション対策（SQLAlchemy ORM）

### 推奨追加対策（本番環境）
- [ ] HTTPS/SSL証明書
- [ ] Basic認証/JWT認証
- [ ] ファイルサイズ制限
- [ ] レート制限

---

## 📚 ドキュメント

1. **README.md** - 概要・クイックスタート
2. **SETUP_GUIDE.md** - 詳細セットアップ手順
3. **PROJECT_SUMMARY.md** - このファイル（技術仕様）
4. **test_setup.py** - セットアップテスト

---

## 🧪 テスト

```bash
# セットアップテスト実行
python test_setup.py

# ヘルスチェック
curl http://localhost:8000/api/health

# 統計API
curl http://localhost:8000/api/statistics
```

---

## 📞 サポート・問い合わせ

### ログ確認
```bash
docker-compose logs -f web
```

### データベースアクセス
```bash
docker-compose exec db psql -U postgres amazon_analytics
```

### コンテナ再起動
```bash
docker-compose restart web
```

---

## 📄 ライセンス

MIT License

---

## 👤 作成者

**Yoshi**  
作成日: 2025年10月21日

---

## 🎉 プロジェクト完成！

要件定義書（REQ-AMAZON-001.md）に基づき、Phase 1〜3の主要機能を**完全実装**しました。

### すぐに使えます！
1. Docker Composeで起動
2. CSVをアップロード
3. AI分析を実行
4. レポートを確認

**Happy Analyzing! 📊💰**

