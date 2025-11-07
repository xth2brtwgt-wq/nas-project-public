# 🔧 502エラー修正 - タイムアウト設定

**作成日**: 2025-11-05  
**対象**: `/upload`エンドポイントでの502 Bad Gatewayエラー

---

## ⚠️ 問題

ファイルアップロード時に502 Bad Gatewayエラーが発生する。

**原因**: Nginx Proxy Managerのタイムアウト設定が短すぎるため、長時間処理（ファイルアップロード、文字起こし、議事録生成）中にタイムアウトが発生している。

---

## ✅ 解決方法

Nginx Proxy ManagerのAdvancedタブにタイムアウト設定とファイルサイズ制限を追加します。

---

## 📋 修正手順

### Step 1: Nginx Proxy ManagerのWeb UIにアクセス

1. **ブラウザで以下にアクセス**:
   ```
   http://YOUR_IP_ADDRESS110:8181
   ```

2. **ログイン**（管理者アカウント）

---

### Step 2: Advancedタブを開く

1. **「Proxy Hosts」タブをクリック**

2. **`yoshi-nas-sys.duckdns.org`を編集**

3. **「Advanced」タブをクリック**

---

### Step 3: タイムアウト設定を追加

既存の「Custom Nginx Configuration」の**最後に**以下を追加：

```nginx
# ==========================================
# タイムアウト設定（ファイルアップロード・長時間処理用）
# ==========================================

# ファイルアップロードサイズ制限（500MB）
client_max_body_size 500M;

# タイムアウト設定（長時間処理対応）
proxy_connect_timeout 600s;
proxy_send_timeout 600s;
proxy_read_timeout 600s;

# バッファ設定（大きなファイルアップロード用）
proxy_request_buffering off;
proxy_buffering off;

# バッファサイズ設定
proxy_buffer_size 128k;
proxy_buffers 4 256k;
proxy_busy_buffers_size 256k;
```

**重要**: 
- 既存の設定を削除しないでください
- 既存の設定の**最後に**追加してください
- 既存の設定と重複しないように注意してください

---

### Step 4: `/meetings`専用のタイムアウト設定を追加（オプション）

より細かい制御が必要な場合、`/meetings`専用のlocationブロックを追加：

```nginx
# /meetings のタイムアウト設定（長時間処理用）
location /meetings/upload {
    proxy_pass http://YOUR_IP_ADDRESS110:5002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # タイムアウト設定（10分）
    proxy_connect_timeout 600s;
    proxy_send_timeout 600s;
    proxy_read_timeout 600s;
    
    # ファイルサイズ制限（500MB）
    client_max_body_size 500M;
    
    # バッファ設定
    proxy_request_buffering off;
    proxy_buffering off;
    
    # WebSocket設定（Socket.IO用）
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    
    auth_basic off;
}
```

**注意**: この設定は既存のCustom Locationの設定と競合する可能性があるため、まずは方法1（全体設定）を試してください。

---

### Step 5: 設定を保存

1. **「Save」をクリック**

2. **30秒待ってからアクセステスト**

---

## 🔍 設定の確認

設定を保存した後、以下を確認してください：

1. **Nginx設定の構文チェック**:
   ```bash
   # NASにSSH接続
   ssh -p 23456 YOUR_USERNAME@YOUR_IP_ADDRESS110
   
   # Nginx設定の構文チェック
   docker exec nginx-proxy-manager nginx -t
   ```

2. **アクセステスト**:
   - `https://yoshi-nas-sys.duckdns.org:8443/meetings`にアクセス
   - ファイルをアップロードして502エラーが発生しないことを確認

---

## 📊 タイムアウト設定の説明

### 推奨設定値

| 設定項目 | 値 | 説明 |
|---------|-----|------|
| `proxy_connect_timeout` | 600s | バックエンドサーバーへの接続タイムアウト（10分） |
| `proxy_send_timeout` | 600s | リクエスト送信タイムアウト（10分） |
| `proxy_read_timeout` | 600s | レスポンス読み取りタイムアウト（10分） |
| `client_max_body_size` | 500M | アップロード可能なファイルサイズ上限（500MB） |

### 処理時間の目安

- **ファイルアップロード**: 数秒〜数十秒（ファイルサイズによる）
- **文字起こし処理**: 1分〜5分（音声ファイルの長さによる）
- **議事録生成**: 30秒〜2分（文字起こし内容による）
- **合計**: 2分〜7分程度

**推奨タイムアウト**: 10分（600秒）は十分な余裕があります。

---

## 🚨 よくある問題

### 問題1: 設定を追加しても502エラーが発生する

**原因**: 設定が正しく反映されていない、または既存の設定と競合している

**解決方法**:
1. Nginx設定の構文チェックを実行
2. Nginx Proxy Managerを再起動
3. ブラウザキャッシュをクリア

---

### 問題2: ファイルサイズが大きすぎる

**原因**: `client_max_body_size`が小さすぎる

**解決方法**:
- `client_max_body_size`を500Mに設定（必要に応じて1Gに増やす）

---

### 問題3: タイムアウトが短すぎる

**原因**: 処理が10分を超える場合

**解決方法**:
- `proxy_read_timeout`を900s（15分）に増やす
- または、アプリケーション側で処理を非同期化する

---

## ✅ チェックリスト

修正後、以下を確認してください：

- [ ] Advancedタブにタイムアウト設定を追加
- [ ] Nginx設定の構文チェックが成功することを確認
- [ ] `https://yoshi-nas-sys.duckdns.org:8443/meetings`にアクセスできることを確認
- [ ] ファイルをアップロードして502エラーが発生しないことを確認
- [ ] 長時間処理（文字起こし、議事録生成）が正常に完了することを確認

---

## 📚 参考資料

- [Nginx Proxy Manager公式ドキュメント](https://nginxproxymanager.com/)
- [Nginx proxy_read_timeout](http://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_read_timeout)
- [Nginx client_max_body_size](http://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size)

---

**作成日**: 2025-11-05  
**更新日**: 2025-11-05









