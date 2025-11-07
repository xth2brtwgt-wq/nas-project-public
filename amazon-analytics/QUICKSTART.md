# Amazon Purchase Analytics - クイックスタート

## 🚀 最速セットアップ（5分）

### 前提条件
- Docker & Docker Compose がインストール済み
- Gemini APIキー（既存システムから流用済み）

---

## ステップ1: プロジェクトディレクトリに移動

```bash
cd /Users/Yoshi/nas-project/amazon-analytics
```

---

## ステップ2: 起動（.env作成済みの場合）

```bash
# ビルド＆起動
./deploy.sh build
```

または手動で：

```bash
docker-compose up -d  # .envを使用します
```

---

## ステップ3: ブラウザでアクセス

```
http://localhost:8000
```

---

## 🎯 使い方

### 1. CSVをアップロード

1. ダッシュボードの「**アップロード**」タブを開く
2. Amazon CSVファイルをドラッグ&ドロップ
   - ファイル: `/Users/Yoshi/Downloads/Your Orders/Retail.OrderHistory.3/Retail.OrderHistory.3.csv`
3. 自動的にデータが取り込まれます

### 2. 統計を確認

- 「**概要**」タブで総支出額、カテゴリ別グラフを確認

### 3. AI分析を実行

「**分析**」タブで：
- ✅ **自動カテゴリ分類** - Gemini AIが商品を自動分類
- ✅ **衝動買い検出** - 短期間での複数購入を警告
- ✅ **定期購入候補** - 繰り返し購入している商品を検出
- ✅ **月次インサイト** - AIが節約アドバイスを生成

### 4. 購入履歴を閲覧

- 「**購入履歴**」タブで詳細リストを表示
- カテゴリでフィルタリング可能

---

## 🔧 便利なコマンド

```bash
# ログ確認
docker-compose logs -f web

# 再起動
./deploy.sh restart

# 停止
./deploy.sh stop

# リビルド
./deploy.sh rebuild

# バージョン確認
curl http://localhost:8000/api/version
```

---

## 📊 設定内容（.env）

```env
# AI Provider
AI_PROVIDER=gemini

# Gemini API（既存システムから流用）
GEMINI_API_KEY=AIzaSyDS_gER_ei9mfkNoGG63P2VODorlayD9dM
GEMINI_MODEL=gemini-2.0-flash-exp

# データベース
POSTGRES_PASSWORD=amazon_analytics_2025

# メール（オプション・既存設定流用）
SMTP_USER=mipatago.netsetting@gmail.com
EMAIL_TO=nas.system.0828@gmail.com
```

---

## 🎉 完了！

これで以下の機能が使えます：

✅ CSV自動取り込み  
✅ Gemini AI自動分類  
✅ 購買パターン分析  
✅ 月次インサイト生成  
✅ グラフ可視化  
✅ レポート出力

---

## 🆘 トラブルシューティング

### データベース接続エラー

```bash
docker-compose restart db
docker-compose logs db
```

### AI分類が動かない

```bash
# Gemini APIキーを確認
cat .env | grep GEMINI_API_KEY

# コンテナを再起動
docker-compose restart web
```

### CSVアップロードエラー

- 正しいファイル（`Retail.OrderHistory.3.csv`）を使用しているか確認
- ファイルサイズが10MB以下か確認

---

## 📚 詳細ドキュメント

- **README.md** - 概要
- **SETUP_GUIDE.md** - 詳細セットアップ
- **PROJECT_SUMMARY.md** - 技術仕様
- **ALTERNATIVE_GEMINI.md** - Gemini API詳細

---

**Happy Analyzing! 📊💰**

