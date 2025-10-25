# 🚀 デプロイメントルール

**作成日**: 2025-10-21  
**適用範囲**: nas-project全プロジェクト

---

## 📋 基本ルール

### 🔒 **絶対ルール: ローカル修正 → NASデプロイ**

**すべての修正は必ず以下の順序で実行する：**

1. **ローカルで修正**
   - コードの変更・修正
   - テスト・動作確認
   - コミット・プッシュ

2. **NASにデプロイ**
   - `git pull`で最新コードを取得
   - コンテナの再ビルド・再起動

---

## ❌ 禁止事項

### 🚫 **NAS上での直接修正は禁止**

```bash
# ❌ 絶対にやってはいけない
ssh YOUR_USERNAME@YOUR_NAS_IP "nano ~/nas-project/amazon-analytics/app/api/main.py"
```

**理由:**
- 変更がGitに反映されない
- 他の環境と不整合が発生
- デプロイ時に変更が失われる

---

## ✅ 正しい手順

### 🔄 **標準デプロイフロー**

```bash
# 1. ローカルで修正
cd /Users/Yoshi/nas-project
# ファイルを編集...

# 2. コミット・プッシュ
git add .
git commit -m "fix: 問題を修正"
git push origin main

# 3. NASでデプロイ
ssh YOUR_USERNAME@YOUR_NAS_IP "cd ~/nas-project && git pull origin main"
ssh YOUR_USERNAME@YOUR_NAS_IP "cd ~/nas-project/[プロジェクト名] && docker compose down && docker compose up -d --build"
```

---

## 🎯 プロジェクト別デプロイコマンド

### Amazon Analytics
```bash
ssh YOUR_USERNAME@YOUR_NAS_IP "cd ~/nas-project/amazon-analytics && docker compose down && docker compose up -d --build"
```

### Document Automation
```bash
ssh YOUR_USERNAME@YOUR_NAS_IP "cd ~/nas-project/document-automation && docker compose down && docker compose up -d --build"
```

### Insta360 Auto Sync
```bash
ssh YOUR_USERNAME@YOUR_NAS_IP "cd ~/nas-project/insta360-auto-sync && docker compose down && docker compose up -d --build"
```

### Meeting Minutes BYC
```bash
ssh YOUR_USERNAME@YOUR_NAS_IP "cd ~/nas-project/meeting-minutes-byc && docker compose down && docker compose up -d --build"
```

---

## 🔧 緊急時の対応

### 🚨 **緊急修正が必要な場合**

1. **一時的な修正**（NAS上）
   ```bash
   # 緊急時のみ許可
   ssh YOUR_USERNAME@YOUR_NAS_IP "cd ~/nas-project/[プロジェクト] && docker compose restart"
   ```

2. **必ず後でローカルに反映**
   ```bash
   # 緊急修正後、必ずローカルで同じ修正を実施
   # コミット・プッシュして正式化
   ```

---

## 📊 デプロイ確認

### ✅ **デプロイ成功の確認**

```bash
# 1. コンテナ状態確認
ssh YOUR_USERNAME@YOUR_NAS_IP "docker ps | grep [プロジェクト名]"

# 2. ログ確認
ssh YOUR_USERNAME@YOUR_NAS_IP "docker logs [コンテナ名] --tail 20"

# 3. ヘルスチェック
curl http://YOUR_NAS_IP:[ポート番号]/
```

---

## 🎓 実例: タイムアウト修正

### 問題
- Amazon分析で「Load failed」エラー
- WORKER TIMEOUTが発生

### 解決手順
```bash
# 1. ローカルで修正
# Dockerfileのタイムアウトを120秒→600秒に変更

# 2. コミット・プッシュ
git add amazon-analytics/Dockerfile
git commit -m "fix: Gunicornタイムアウトを600秒に延長"
git push origin main

# 3. NASでデプロイ
ssh YOUR_USERNAME@YOUR_NAS_IP "cd ~/nas-project && git pull origin main"
ssh YOUR_USERNAME@YOUR_NAS_IP "cd ~/nas-project/amazon-analytics && docker compose down && docker compose up -d --build"
```

---

## 💡 まとめ

### 🎯 **このルールの重要性**

1. **一貫性の確保**
   - 全環境で同じコードが動作
   - 設定の不整合を防止

2. **変更履歴の管理**
   - すべての変更がGitで追跡可能
   - ロールバックが容易

3. **チーム開発の効率化**
   - 他のメンバーも同じ手順でデプロイ可能
   - 混乱を防止

---

**⚠️ 重要: このルールは絶対に守る。NAS上での直接修正は禁止。**
