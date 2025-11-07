# 🔧 Nginx Proxy Manager 502エラー修正手順

**作成日**: 2025-11-05  
**対象**: meeting-minutes-byc の502 Bad Gatewayエラー

---

## 📋 診断結果

✅ **アプリケーションは正常に動作しています**
- コンテナは起動中（healthy）
- ポート5002は正常に動作
- ヘルスチェックは成功
- Nginx Proxy Managerからアプリケーションへの接続は成功

❌ **502エラーが発生している原因**: Nginx Proxy Managerの設定問題

---

## ✅ 修正手順

### Step 1: Nginx Proxy ManagerのWeb UIにアクセス

1. **ブラウザで以下にアクセス**:
   ```
   http://YOUR_IP_ADDRESS110:8181
   ```

2. **ログイン**（管理者アカウント）

---

### Step 2: `/meetings` Custom Locationの設定を確認・修正

1. **「Proxy Hosts」タブをクリック**

2. **`yoshi-nas-sys.duckdns.org`を編集**

3. **「Custom Locations」タブをクリック**

4. **`/meetings`のLocationを編集**（歯車アイコン⚙️をクリック）

---

### Step 3: 基本設定を確認

以下の設定を確認してください：

#### ✅ 正しい設定

| 項目 | 値 |
|------|-----|
| **Define location** | `/meetings` |
| **Scheme** | `http` |
| **Forward Hostname/IP** | `YOUR_IP_ADDRESS110/` **（末尾にスラッシュ必須）** |
| **Forward Port** | `5002` |
| **Websockets Support** | ✅ **オン（必須）** |
| **Block Common Exploits** | ✅ オン |
| **Cache Assets** | ✅ オン（オプション） |

---

### Step 4: Custom Nginx configurationを設定

**「Custom Nginx configuration」テキストエリア**に以下を記述：

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_read_timeout 300s;
proxy_connect_timeout 300s;
proxy_send_timeout 300s;
```

**重要**: この設定はSocket.IO（WebSocket）を使用するために必須です。

---

### Step 5: 設定を保存

1. **「Save」をクリック**（Custom Locationの保存）

2. **「Details」タブに戻る**

3. **「Save」をクリック**（Proxy Host全体の保存）

---

### Step 6: Nginx Proxy Managerを再起動（必要に応じて）

設定が反映されない場合は、Nginx Proxy Managerを再起動：

```bash
# NASにSSH接続
ssh -p 23456 YOUR_USERNAME@YOUR_IP_ADDRESS110

# Nginx Proxy Managerを再起動
docker restart nginx-proxy-manager
```

---

## 🔍 確認手順

### 1. Proxy Hostのステータス確認

Nginx Proxy ManagerのWeb UIで：
- `yoshi-nas-sys.duckdns.org`のステータスが「**Online**」になっていることを確認

### 2. アクセステスト

ブラウザで以下にアクセス：
```
https://yoshi-nas-sys.duckdns.org:8443/meetings
```

**期待される結果**:
- ✅ ページが正常に表示される
- ✅ 502エラーが発生しない

### 3. WebSocket接続の確認

ブラウザの開発者ツール（F12）で：
- Networkタブを開く
- `/socket.io/`へのリクエストが成功していることを確認

---

## 🚨 よくある問題と対処法

### 問題1: Forward Hostname/IPの末尾にスラッシュがない

**症状**: 404エラーまたは502エラー

**解決方法**:
- Forward Hostname/IPを`YOUR_IP_ADDRESS110`から`YOUR_IP_ADDRESS110/`に変更（末尾にスラッシュを追加）

---

### 問題2: Websockets Supportがオフになっている

**症状**: Socket.IO接続エラー、WebSocketエラー

**解決方法**:
- Custom Locationの「Websockets Support」を**オン**にする

---

### 問題3: Custom Nginx configurationが空欄

**症状**: WebSocket接続が失敗する

**解決方法**:
- Step 4のCustom Nginx configurationを追加

---

### 問題4: タイムアウトエラー

**症状**: 長時間の処理で502エラーが発生

**解決方法**:
- Custom Nginx configurationにタイムアウト設定を追加：
  ```nginx
  proxy_read_timeout 300s;
  proxy_connect_timeout 300s;
  proxy_send_timeout 300s;
  ```

---

## 📊 設定確認コマンド

NAS上で以下を実行して、設定が正しく反映されているか確認：

```bash
# Nginx設定の構文チェック
docker exec nginx-proxy-manager nginx -t

# Nginx Proxy Managerのログ確認
docker logs nginx-proxy-manager --tail 50 | grep -i "error\|502"

# Nginx Proxy Managerからアプリケーションへの接続テスト
docker exec nginx-proxy-manager curl -I http://YOUR_IP_ADDRESS110:5002/health
```

---

## ✅ チェックリスト

修正後、以下を確認してください：

- [ ] Forward Hostname/IPが`YOUR_IP_ADDRESS110/`（末尾にスラッシュ）になっている
- [ ] Forward Portが`5002`になっている
- [ ] Websockets Supportが**オン**になっている
- [ ] Custom Nginx configurationが設定されている
- [ ] Proxy Hostのステータスが「**Online**」になっている
- [ ] `https://yoshi-nas-sys.duckdns.org:8443/meetings`にアクセスできる
- [ ] 502エラーが発生しない

---

## 📚 参考資料

- [Nginx Proxy Manager公式ドキュメント](https://nginxproxymanager.com/)
- [NGINX_PROXY_MANAGER_CUSTOM_LOCATION_PATH_FIX.md](../../docs/deployment/NGINX_PROXY_MANAGER_CUSTOM_LOCATION_PATH_FIX.md)
- [NGINX_PROXY_MANAGER_CUSTOM_LOCATIONS_SUMMARY.md](../../docs/deployment/NGINX_PROXY_MANAGER_CUSTOM_LOCATIONS_SUMMARY.md)

---

**作成日**: 2025-11-05  
**更新日**: 2025-11-05









