# ✅ YouTube to Notion 認証機能 起動確認

**作成日**: 2025-11-04  
**目的**: 再ビルド後の起動ログと認証機能を確認

---

## ❌ 問題

再ビルド後、起動直後に接続がリセットされています：

```
* Recv failure: Connection reset by peer
* Closing connection 0
curl: (56) Recv failure: Connection reset by peer
```

これは、アプリケーションがまだ起動していない可能性があります。

---

## ✅ 確認手順

### ステップ1: コンテナの状態を確認

```bash
cd ~/nas-project/youtube-to-notion
sudo docker compose ps
```

### ステップ2: 起動ログを確認（認証関連）

```bash
sudo docker compose logs youtube-to-notion | grep -i "認証\|auth\|AUTH"
```

### ステップ3: 起動ログ全体を確認（最新100行）

```bash
sudo docker compose logs youtube-to-notion --tail 100
```

### ステップ4: コンテナのヘルスチェック

```bash
# 少し待ってから再試行
sleep 5
curl http://localhost:8111/health
```

### ステップ5: 直接アクセスして認証を確認

```bash
curl -v http://localhost:8111/
```

**期待される動作**:
- ヘルスチェックは正常に応答する（認証不要）
- ルートエンドポイント（`/`）にアクセスすると、HTTP 307が返ってきて、ログインページにリダイレクトされる

### ステップ6: ブラウザで確認

1. **ダッシュボードにログインしていない状態で**、`http://192.168.68.110:8111/`にアクセス
2. ログインページにリダイレクトされることを確認

3. **ダッシュボードにログインした後**、`http://192.168.68.110:8111/`にアクセス
4. YouTube画面が表示されることを確認

---

## 📝 クイックコマンド（一括実行）

```bash
cd ~/nas-project/youtube-to-notion

# 1. コンテナの状態を確認
echo "=== コンテナの状態を確認 ==="
sudo docker compose ps

# 2. 起動ログを確認（認証関連）
echo ""
echo "=== 起動ログを確認（認証関連） ==="
sudo docker compose logs youtube-to-notion | grep -i "認証\|auth\|AUTH"

# 3. 起動ログ全体を確認（最新100行）
echo ""
echo "=== 起動ログ全体を確認（最新100行） ==="
sudo docker compose logs youtube-to-notion --tail 100

# 4. 少し待ってからヘルスチェック
echo ""
echo "=== ヘルスチェック ==="
sleep 5
curl http://localhost:8111/health

# 5. 直接アクセスして認証を確認
echo ""
echo "=== 直接アクセスして認証を確認 ==="
curl -v http://localhost:8111/
```

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

