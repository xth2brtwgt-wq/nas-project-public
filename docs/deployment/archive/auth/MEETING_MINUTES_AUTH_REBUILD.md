# 🔧 Meeting Minutes BYC 認証機能 完全再ビルド手順

**作成日**: 2025-11-04  
**目的**: 認証機能が動作しない場合の完全再ビルド

---

## ❌ 問題

認証モジュールのインポートは成功しているが、実際のリクエストで認証チェックが実行されていない。

---

## ✅ 解決方法: 完全再ビルド

### ステップ1: コンテナを停止・削除

```bash
cd ~/nas-project/meeting-minutes-byc
sudo docker compose down
```

### ステップ2: イメージを再ビルド

```bash
cd ~/nas-project/meeting-minutes-byc
sudo docker compose build --no-cache
```

### ステップ3: コンテナを起動

```bash
sudo docker compose up -d
```

### ステップ4: 起動ログを確認

```bash
sudo docker compose logs -f meeting-minutes-byc
```

以下のようなログが表示されることを確認：

```
認証モジュールを読み込みました
サブフォルダ対応を有効化: APPLICATION_ROOT=/meetings
```

### ステップ5: 実際のリクエストログを確認

別ターミナルで以下を実行：

```bash
cd ~/nas-project/meeting-minutes-byc
sudo docker compose logs -f meeting-minutes-byc
```

ブラウザで直接アクセス（未認証）して、以下のようなログが表示されるか確認：

```
[AUTH] 認証が必要です: / -> http://192.168.68.110:9001/login
```

---

## 🔍 確認項目

### 再ビルド後の確認

1. **起動ログに「認証モジュールを読み込みました」が表示される**
2. **未認証でアクセスした場合、ログインページにリダイレクトされる**
3. **ログに「[AUTH] 認証が必要です」が表示される**

---

## 🔧 トラブルシューティング

### 再ビルド後も認証が機能しない場合

1. **最新コードを確認**:
   ```bash
   cd ~/nas-project/meeting-minutes-byc
   git log --oneline -5
   git status
   ```

2. **app.pyの内容を確認**:
   ```bash
   grep -n "@require_auth\|AUTH_ENABLED" app.py
   ```

3. **コンテナ内のapp.pyを確認**:
   ```bash
   sudo docker compose exec meeting-minutes-byc grep -n "@require_auth\|AUTH_ENABLED" /app/app.py
   ```

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

