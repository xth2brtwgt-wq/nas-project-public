# 🔍 ダッシュボード認証 ログ確認手順

**作成日**: 2025-11-04  
**目的**: 認証関連のログが表示されない問題の確認と修正

---

## ❌ 問題

認証関連のログが表示されない：

```bash
sudo docker compose logs nas-dashboard | grep -i "認証\|auth\|session\|login" | tail -20
# 何も表示されない
```

---

## 🔍 原因の可能性

1. **アプリケーションが再起動されていない**
   - 古いコードが実行されている可能性

2. **ログレベルが低い**
   - `logger.debug()`が出力されない可能性

3. **アプリケーションがエラーで起動していない**
   - 起動時にエラーが発生している可能性

---

## ✅ 確認手順

### ステップ1: アプリケーションの状態確認

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose ps
```

コンテナが起動していることを確認してください。

### ステップ2: 最新コードのプルと再起動

```bash
cd ~/nas-project/nas-dashboard
git pull origin feature/monitoring-fail2ban-integration
sudo docker compose down
sudo docker compose up -d
```

### ステップ3: アプリケーションのログを確認

```bash
cd ~/nas-project/nas-dashboard

# すべてのログを確認（最新50行）
sudo docker compose logs nas-dashboard | tail -50

# エラーログを確認
sudo docker compose logs nas-dashboard | grep -i "error\|exception" | tail -20

# 起動時のログを確認
sudo docker compose logs nas-dashboard | grep -i "認証\|init\|start" | tail -20
```

### ステップ4: ブラウザでアクセスしてログを確認

1. ブラウザでアクセス：
   - **外部アクセス**: `https://yoshi-nas-sys.duckdns.org:8443/`
   - **内部アクセス**: `http://192.168.68.110:9001/`

2. アクセス後、ログを確認：

```bash
cd ~/nas-project/nas-dashboard

# 最新のログを確認
sudo docker compose logs nas-dashboard --tail 50

# 認証関連のログを確認（INFOレベル以上）
sudo docker compose logs nas-dashboard | grep -i "\[AUTH\]" | tail -20
```

### ステップ5: ログレベルを確認

ログレベルが`DEBUG`になっているか確認：

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose exec nas-dashboard python -c "
import os
import logging

print(f'ログレベル: {logging.getLogger().level}')
print(f'LOG_LEVEL環境変数: {os.getenv(\"LOG_LEVEL\", \"未設定\")}')
"
```

---

## 🔧 修正方法

### 方法1: アプリケーションを完全に再起動

```bash
cd ~/nas-project/nas-dashboard
sudo docker compose down
sudo docker compose up -d
```

### 方法2: ログレベルをDEBUGに設定

`.env`ファイルに以下を追加：

```bash
LOG_LEVEL=DEBUG
```

その後、アプリケーションを再起動：

```bash
sudo docker compose restart nas-dashboard
```

### 方法3: 直接ログを確認

```bash
cd ~/nas-project/nas-dashboard

# リアルタイムでログを確認
sudo docker compose logs -f nas-dashboard
```

別のターミナルでブラウザからアクセスして、ログを確認してください。

---

## 📝 確認項目

- [ ] アプリケーションが起動している
- [ ] 最新コードがプルされている
- [ ] アプリケーションが再起動されている
- [ ] ログにエラーが表示されていない
- [ ] ブラウザでアクセスした後、ログに何か表示される

---

## 🎯 期待されるログ

ブラウザでアクセスした後、以下のようなログが表示されるはずです：

```
[AUTH] セッションIDがありません
[AUTH] 認証が必要です: /
```

または、既にログインしている場合：

```
[AUTH] ユーザー認証成功: admin (user_id: 1)
```

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

