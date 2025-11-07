# 📋 youtube-to-notion サブフォルダ対応デプロイ手順

**作成日**: 2025-11-04  
**目的**: `youtube-to-notion`をサブフォルダ（`/youtube`）で動作させるためのデプロイ手順

---

## 📋 前提条件

- ✅ `youtube-to-notion`のコードがGitにプッシュ済み
- ✅ NAS上でGitリポジトリをプル済み
- ✅ Nginx Proxy Managerが設定済み（`yoshi-nas-sys.duckdns.org`のProxy Hostが存在）

---

## 🚀 デプロイ手順

### ステップ1: NAS上でGitリポジトリを更新

```bash
# NASにSSH接続
ssh AdminUser@192.168.68.110

# youtube-to-notionディレクトリに移動
cd /home/AdminUser/nas-project/youtube-to-notion

# 最新のコードを取得
git pull origin feature/monitoring-fail2ban-integration
```

### ステップ2: 環境変数を設定

`.env`ファイルに以下を追加：

```bash
# Subfolder Support (Optional)
# Nginx Proxy Manager経由でサブフォルダ（/youtube）でアクセスする場合に設定
# 内部ネットワークから直接アクセスする場合は設定不要（空欄のまま）
SUBFOLDER_PATH=/youtube
```

**注意**: `.env.local`は使用しないため、`.env`ファイルに直接追加してください。

### ステップ3: Dockerコンテナを再ビルド・再起動

```bash
# コンテナを停止
sudo docker compose down

# イメージを再ビルド（コード変更があるため）
sudo docker compose build --no-cache

# コンテナを起動
sudo docker compose up -d

# ログを確認
sudo docker compose logs -f
```

### ステップ4: Nginx Proxy Managerの設定を更新

1. **Nginx Proxy ManagerのWeb UIにアクセス**
   - URL: `http://192.168.68.110:8181`
   - Proxy Hosts → `yoshi-nas-sys.duckdns.org` を選択

2. **Custom Locationsタブを確認**
   - `/youtube` のCustom Locationが存在することを確認
   - 存在しない場合は、以下を追加：
     - **Location**: `/youtube`
     - **Scheme**: `http`
     - **Forward Hostname/IP**: `192.168.68.110:8111`（末尾にスラッシュなし）
     - **Forward Port**: `8111`
     - **Websockets Support**: ✅ チェック（歯車アイコンから設定）

3. **Advancedタブに設定を追加**
   - 既存の設定に以下を追加：

```nginx
# /youtube の静的ファイル修正（youtube-to-notion）
location ^~ /youtube/static/ {
    rewrite ^/youtube/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:8111;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /youtube のSocket.IO修正（youtube-to-notion）
location ~ ^/youtube/socket.io/(.*)$ {
    rewrite ^/youtube/socket.io/(.*)$ /socket.io/$1 break;
    proxy_pass http://192.168.68.110:8111;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    auth_basic off;
}

# /youtube のAPI修正（youtube-to-notion）
location ~ ^/youtube/api/(.*)$ {
    rewrite ^/youtube/api/(.*)$ /api/$1 break;
    proxy_pass http://192.168.68.110:8111;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}
```

4. **Saveをクリック**
   - Proxy Hostのステータスが「Online」のままであることを確認
   - 「Offline」になった場合は、設定に構文エラーがある可能性があります

### ステップ5: 動作確認

1. **外部アクセスで確認**
   - URL: `https://yoshi-nas-sys.duckdns.org:8443/youtube`
   - ブラウザの開発者ツール（F12）→ Networkタブを開く

2. **確認項目**
   - ✅ `favicon.svg`が正常に読み込まれる（200 OK）
   - ✅ Socket.IO接続が正常に確立される（404エラーが出ない）
   - ✅ APIリクエスト（`/api/youtube/process`など）が正常に動作する（200 OK）

3. **内部アクセスで確認**
   - URL: `http://192.168.68.110:8111`
   - 内部アクセスでも正常に動作することを確認（環境変数`SUBFOLDER_PATH`が設定されている場合、静的ファイルのパスが`/youtube/static/...`になる可能性があります）

---

## ⚠️ トラブルシューティング

### Socket.IO接続が404エラーになる場合

1. **Nginx Proxy ManagerのAdvancedタブの設定を確認**
   - `/youtube/socket.io/`のリライト設定が正しく追加されているか
   - `proxy_http_version 1.1;`と`Upgrade`、`Connection`ヘッダーが設定されているか

2. **Custom LocationのWebsocket Supportを確認**
   - `/youtube`のCustom Locationで「Websockets Support」が有効になっているか

3. **Nginx設定の構文チェック**
   ```bash
   sudo docker exec nginx-proxy-manager nginx -t
   ```

4. **Nginx設定の再読み込み**
   ```bash
   sudo docker exec nginx-proxy-manager nginx -s reload
   ```

### 静的ファイルが404エラーになる場合

1. **Nginx Proxy ManagerのAdvancedタブの設定を確認**
   - `/youtube/static/`のリライト設定が正しく追加されているか
   - `location ^~ /youtube/static/`が他の設定より前に記述されているか

2. **アプリケーション側の設定を確認**
   - `.env`ファイルに`SUBFOLDER_PATH=/youtube`が設定されているか
   - Dockerコンテナのログで`SUBFOLDER_PATH`が正しく読み込まれているか確認:
     ```bash
     sudo docker compose logs youtube-to-notion | grep SUBFOLDER_PATH
     ```

### APIリクエストが404エラーになる場合

1. **Nginx Proxy ManagerのAdvancedタブの設定を確認**
   - `/youtube/api/`のリライト設定が正しく追加されているか

2. **アプリケーション側の設定を確認**
   - JavaScript側で`apiPath()`関数が正しく使用されているか
   - ブラウザの開発者ツールで、実際に送信されているAPIリクエストのURLを確認
   - コンテナのログでエラーが出ていないか確認:
     ```bash
     sudo docker compose logs youtube-to-notion --tail=50
     ```

---

## ✅ 完了チェックリスト

- [ ] NAS上でGitリポジトリを更新
- [ ] `.env`ファイルに`SUBFOLDER_PATH=/youtube`を追加
- [ ] Dockerコンテナを再ビルド・再起動
- [ ] Nginx Proxy ManagerのCustom Locationに`/youtube`を追加（Websocket Support有効）
- [ ] Nginx Proxy ManagerのAdvancedタブに`/youtube`の設定を追加
- [ ] `https://yoshi-nas-sys.duckdns.org:8443/youtube`で動作確認
- [ ] Socket.IO接続が正常に確立されることを確認
- [ ] APIリクエストが正常に動作することを確認
- [ ] 静的ファイルが正常に読み込まれることを確認

---

## 📚 参考資料

- [Nginx Proxy Manager Advancedタブ完全設定](NGINX_PROXY_MANAGER_ADVANCED_TAB_COMPLETE_CONFIG.md)
- [meeting-minutes-byc サブフォルダ対応完了](MEETING_MINUTES_SUBFOLDER_DEPLOY_COMPLETE.md)

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

