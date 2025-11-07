# nas-dashboard-monitoring 502エラー修正手順

## ✅ コンテナ起動確認

コンテナが正常に起動していることを確認しました：
- ✅ frontend: ポート3002
- ✅ backend: ポート8002
- ✅ postgres: 起動中
- ✅ redis: 起動中

## 次の確認手順

### 1. ポートへの直接アクセステスト

```bash
# フロントエンド（ポート3002）へのアクセステスト
curl -I http://192.168.68.110:3002

# バックエンド（ポート8002）へのアクセステスト
curl -I http://192.168.68.110:8002
```

**期待される結果**: HTTP 200 OK が返ること

### 2. Nginx Proxy Managerの設定確認

1. **Nginx Proxy ManagerのWeb UIにアクセス**
   - `http://192.168.68.110:8181`

2. **Proxy Hostsタブ** → `yoshi-nas-sys.duckdns.org` を編集

3. **Custom Locationsタブ** → `/monitoring` の設定を確認：
   - **Define location**: `/monitoring`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `192.168.68.110`
   - **Forward Port**: `3002`
   - **Websockets Support**: オン（必須）

4. **Custom Nginx configuration**（歯車アイコン⚙️をクリック）に以下があることを確認：
   ```nginx
   proxy_http_version 1.1;
   proxy_set_header Upgrade $http_upgrade;
   proxy_set_header Connection "upgrade";
   proxy_set_header Host $host;
   proxy_set_header X-Real-IP $remote_addr;
   proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
   proxy_set_header X-Forwarded-Proto $scheme;
   ```

5. **設定を再保存**（Nginxを再読み込み）

### 3. Nginx Proxy Managerコンテナの再起動（オプション）

設定を再保存しても502エラーが続く場合：

```bash
docker restart nginx-proxy-manager
```

### 4. ブラウザでアクセステスト

`https://yoshi-nas-sys.duckdns.org:8443/monitoring` にアクセスして、502エラーが解消されているか確認してください。
