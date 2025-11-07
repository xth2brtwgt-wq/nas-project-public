# 🔍 meeting-minutes-byc - コンテナ状態確認

**作成日**: 2025-11-02  
**目的**: アプリケーションに接続できない問題の解決

---

## ✅ 確認結果

### デプロイ状況
- ✅ 最新コードを取得: 成功
- ✅ 環境変数: `SUBFOLDER_PATH=/meetings`が設定されている
- ✅ Dockerコンテナを再ビルド・再起動: 成功
- ✅ 静的ファイルの存在: `style.css`と`app.js`が存在する
- ❌ アプリケーションに直接アクセス: 接続エラー（`Failed to connect to 192.168.68.110 port 5002`）

---

## 🔍 コンテナ状態の確認

### ステップ1: コンテナの状態を確認

```bash
# コンテナの状態を確認
docker ps | grep meeting-minutes

# または、すべてのコンテナを確認
docker ps -a | grep meeting-minutes
```

### ステップ2: アプリケーションのログを確認

```bash
# アプリケーションのログを確認
docker logs meeting-minutes-byc --tail 100

# リアルタイムでログを監視
docker logs meeting-minutes-byc -f
```

### ステップ3: コンテナが起動しているか確認

```bash
# コンテナの状態を確認
docker inspect meeting-minutes-byc | grep -A 10 "State"

# コンテナのポートマッピングを確認
docker port meeting-minutes-byc
```

### ステップ4: アプリケーションがリッスンしているか確認

```bash
# コンテナ内でポート5002がリッスンしているか確認
docker exec meeting-minutes-byc netstat -tlnp | grep 5002

# または、curlで確認
docker exec meeting-minutes-byc curl -I http://localhost:5002/health
```

---

## 🐛 トラブルシューティング

### コンテナが起動していない場合

#### 1. コンテナを再起動

```bash
docker compose restart meeting-minutes-byc
```

#### 2. コンテナのログを確認

```bash
docker logs meeting-minutes-byc --tail 100
```

エラーメッセージを確認して、問題を特定します。

### アプリケーションが起動していない場合

#### 1. 環境変数を確認

```bash
# コンテナ内の環境変数を確認
docker exec meeting-minutes-byc env | grep -E "(SUBFOLDER_PATH|FLASK|PORT)"
```

#### 2. アプリケーションのプロセスを確認

```bash
# コンテナ内でプロセスを確認
docker exec meeting-minutes-byc ps aux | grep python
```

#### 3. ポートが正しくマッピングされているか確認

```bash
# docker-compose.ymlを確認
cat docker-compose.yml | grep -A 10 "ports"
```

### ポート5002に接続できない場合

#### 1. ホスト側のポートを確認

```bash
# ホスト側でポート5002がリッスンしているか確認
netstat -tlnp | grep 5002

# または、ssで確認
ss -tlnp | grep 5002
```

#### 2. ファイアウォールを確認

```bash
# ファイアウォールの状態を確認
sudo ufw status
```

#### 3. docker-compose.ymlのポートマッピングを確認

`docker-compose.yml`でポート5002が正しくマッピングされているか確認：

```yaml
ports:
  - "5002:5000"
```

---

## 📝 チェックリスト

- [ ] コンテナの状態を確認（起動しているか）
- [ ] アプリケーションのログを確認（エラーがないか）
- [ ] コンテナが起動しているか確認
- [ ] アプリケーションがリッスンしているか確認（ポート5002）
- [ ] ホスト側のポートを確認（ポート5002がマッピングされているか）
- [ ] 環境変数を確認（SUBFOLDER_PATHが設定されているか）
- [ ] docker-compose.ymlのポートマッピングを確認

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant


