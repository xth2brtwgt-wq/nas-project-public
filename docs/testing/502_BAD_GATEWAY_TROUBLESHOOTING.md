# 502 Bad Gateway トラブルシューティング

## 確認手順

### 1. nas-dashboardコンテナの状態確認

```bash
# コンテナが起動しているか確認
docker ps | grep nas-dashboard

# コンテナのログを確認
docker logs nas-dashboard --tail 50

# コンテナの状態を詳細確認
docker inspect nas-dashboard | grep -A 10 "Status"
```

**期待される結果**:
- コンテナが「Up」状態であること
- ログにエラーがないこと

### 2. ポート9001への直接アクセステスト

```bash
# 内部からアクセステスト
curl -I http://192.168.68.110:9001

# レスポンス時間を確認
time curl -I http://192.168.68.110:9001
```

**期待される結果**:
- HTTP 200 OK が返ること
- レスポンスが30秒以内（タイムアウトしないこと）

### 3. nas-dashboardコンテナの再起動

```bash
cd ~/nas-project/nas-dashboard
docker compose restart

# または完全に再起動
docker compose down
docker compose up -d
```

### 4. Nginx Proxy Managerの設定確認

1. **Nginx Proxy ManagerのWeb UIにアクセス**
   - `http://192.168.68.110:8181`

2. **Proxy Hostsタブを開く**

3. **`yoshi-nas-sys.duckdns.org`の設定を確認**:
   - **Detailsタブ**:
     - Domain Names: `yoshi-nas-sys.duckdns.org`
     - Scheme: `http`
     - Forward Hostname/IP: `192.168.68.110`
     - Forward Port: `9001`
   
   - **Custom Locationsタブ**:
     - `/`（ルート）のLocationが存在することを確認
     - Custom Locationsの設定が正しいことを確認

4. **設定を再保存**（Nginxを再読み込み）

### 5. Nginx Proxy Managerコンテナの再起動

```bash
docker restart nginx-proxy-manager
```

### 6. ネットワーク接続確認

```bash
# Nginx Proxy Managerコンテナから転送先への接続をテスト
docker exec nginx-proxy-manager curl -I http://192.168.68.110:9001
```

## よくある原因

1. **nas-dashboardコンテナが停止している**
2. **再ビルド後にコンテナが起動していない**
3. **ポート9001が開いていない**
4. **Nginx Proxy Managerの設定が正しくない**
5. **タイムアウト設定が短すぎる**

