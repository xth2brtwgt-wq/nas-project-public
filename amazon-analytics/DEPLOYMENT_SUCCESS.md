# ✅ Amazon Purchase Analytics デプロイ成功！

## 🎉 セットアップ完了

**日時**: 2025年10月21日  
**バージョン**: 1.0.0 (Build 1)  
**AI Provider**: Gemini API  

---

## ✅ 完了した作業

### 1. Docker環境構築
- ✅ Apple Silicon版Docker Desktop (v28.5.1) インストール
- ✅ Intel版から正しく切り替え完了

### 2. アプリケーションデプロイ
- ✅ PostgreSQL + Redis起動
- ✅ Web アプリケーション起動
- ✅ Gemini APIキー設定完了
- ✅ カテゴリマスタ初期化完了

### 3. 環境変数設定
```env
AI_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyDS_gER_ei9mfkNoGG63P2VODorlayD9dM
GEMINI_MODEL=gemini-2.0-flash-exp
POSTGRES_PASSWORD=amazon_analytics_2025
```

---

## 🌐 アクセス情報

### ダッシュボード
```
http://localhost:8000
```

### API エンドポイント
```
Health Check: http://localhost:8000/api/health
Statistics:    http://localhost:8000/api/statistics
Version:       http://localhost:8000/api/version
Categories:    http://localhost:8000/api/categories
```

---

## 📊 使い方

### 1. CSVをアップロード

**場所**: `/Users/Yoshi/Downloads/Your Orders/Retail.OrderHistory.3/Retail.OrderHistory.3.csv`

**手順**:
1. ブラウザで http://localhost:8000 にアクセス
2. 「アップロード」タブをクリック
3. CSVファイルをドラッグ&ドロップ
4. 自動的にデータが取り込まれます

### 2. AI分析を実行

「**分析**」タブで以下が使えます：

#### 自動カテゴリ分類
- Gemini AIが商品名から自動分類
- 9つのカテゴリに振り分け

#### 衝動買い検出
- 1週間に3回以上の購入を検出
- カテゴリ別に警告表示

#### 定期購入候補
- 繰り返し購入している商品を検出
- 定期便への切り替え提案

#### 月次インサイト
- 年月を指定してAI分析
- 節約アドバイスを生成

### 3. レポート確認

「**概要**」タブで：
- 総支出額
- カテゴリ別円グラフ
- 購入件数

「**購入履歴**」タブで：
- 詳細な購入リスト
- カテゴリフィルタ
- 検索機能

---

## 🔧 管理コマンド

### アプリケーション管理

```bash
cd /Users/Yoshi/nas-project/amazon-analytics

# 再起動
./deploy.sh restart

# ログ確認
./deploy.sh logs

# 停止
./deploy.sh stop

# リビルド
./deploy.sh rebuild
```

### Docker Compose

```bash
cd /Users/Yoshi/nas-project/amazon-analytics

# 起動
docker-compose up -d

# 停止
docker-compose down

# ログ
docker-compose logs -f web
```

### データベース直接アクセス

```bash
docker-compose exec db psql -U postgres amazon_analytics
```

---

## 🧪 動作確認

### ヘルスチェック
```bash
curl http://localhost:8000/api/health
# → {"status":"healthy","version":"1.0.0","app":"Amazon Purchase Analytics"}
```

### バージョン情報
```bash
curl http://localhost:8000/api/version
```

### 統計情報
```bash
curl http://localhost:8000/api/statistics
```

### カテゴリ一覧
```bash
curl http://localhost:8000/api/categories
```

---

## 📝 設定ファイル

### .env（git管理外）
```
/Users/Yoshi/nas-project/amazon-analytics/.env
```

このファイルには実際のAPIキーが含まれています。
**gitプル時も初期化されません**。

---

## 🔄 次回起動方法

```bash
# Docker Desktopが起動していることを確認
docker --version

# Amazon Analyticsを起動
cd /Users/Yoshi/nas-project/amazon-analytics
docker-compose --env-file .env up -d

# ブラウザでアクセス
open http://localhost:8000
```

---

## 🎯 主な機能

### AI分析（Gemini搭載）
- ✅ 自動カテゴリ分類
- ✅ 購買パターン分析
- ✅ 衝動買い検出
- ✅ 定期購入候補提案
- ✅ 月次インサイト生成

### データ管理
- ✅ CSV自動取り込み
- ✅ 重複データ除外
- ✅ カテゴリ別集計
- ✅ 月別推移グラフ
- ✅ CSVエクスポート

### Webダッシュボード
- ✅ レスポンシブデザイン
- ✅ リアルタイム統計
- ✅ Chart.jsグラフ
- ✅ ドラッグ&ドロップアップロード

---

## 📊 データベース情報

### PostgreSQL
- **ホスト**: localhost (コンテナ内)
- **ポート**: 5432
- **データベース**: amazon_analytics
- **ユーザー**: postgres
- **パスワード**: amazon_analytics_2025

### Redis
- **ホスト**: localhost (コンテナ内)
- **ポート**: 6379

---

## 🆘 トラブルシューティング

### ポート衝突エラー
```bash
# 8000番ポートを使用しているプロセスを確認
lsof -i :8000

# 停止してから再起動
./deploy.sh stop
./deploy.sh restart
```

### データベース接続エラー
```bash
# DBコンテナのログ確認
docker-compose logs db

# DBコンテナ再起動
docker-compose restart db
```

### Gemini API エラー
```bash
# 環境変数確認
docker-compose exec web env | grep GEMINI

# コンテナ再起動
docker-compose --env-file .env restart web
```

---

## 📚 ドキュメント

1. **QUICKSTART.md** - クイックスタートガイド
2. **README.md** - プロジェクト概要
3. **SETUP_GUIDE.md** - 詳細セットアップ手順
4. **PROJECT_SUMMARY.md** - 技術仕様
5. **GEMINI_SETUP_COMPLETE.md** - Gemini API対応完了報告
6. **DEPLOYMENT_SUCCESS.md** - このファイル

---

## 🎉 成功！

Amazon Purchase Analyticsシステムが正常に起動しました！

**今すぐ使えます:**
```
http://localhost:8000
```

CSVファイルをアップロードして、AI分析を試してみてください！

---

**デプロイ完了日時**: 2025年10月21日  
**ステータス**: ✅ 稼働中  
**AI Provider**: Gemini API (gemini-2.0-flash-exp)

