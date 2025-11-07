# 🔧 Nginx Proxy Manager オフライン修正手順

**作成日**: 2025-11-05  
**対象**: Custom Nginx configuration追加でProxy Hostがオフラインになった場合

---

## ⚠️ 問題

Custom Nginx configurationを追加したら、Proxy Hostのステータスが「Offline」になった。

---

## 🔍 原因の確認

まず、Nginx設定の構文エラーを確認します。

### Step 1: Nginx設定の構文チェック

NASにSSH接続して以下を実行：

```bash
# NASにSSH接続
ssh -p 23456 YOUR_USERNAME@YOUR_IP_ADDRESS110

# Nginx設定の構文チェック
docker exec nginx-proxy-manager nginx -t
```

**エラーが表示される場合**: 構文エラーが原因です。

**期待される出力**:
```
nginx: the configuration file /etc/nginx/nginx.conf test is successful
```

### Step 2: Nginx Proxy Managerのログ確認

```bash
# Nginx Proxy Managerのログを確認
docker logs nginx-proxy-manager --tail 100 | grep -i "error\|syntax"
```

---

## ✅ 段階的な修正手順

### Step 1: Custom Nginx configurationをクリア（緊急対応）

まず、設定をクリアしてProxy Hostをオンラインに戻します。

1. **Nginx Proxy ManagerのWeb UI**: `http://YOUR_IP_ADDRESS110:8181`

2. **「Proxy Hosts」タブ → `yoshi-nas-sys.duckdns.org`を編集**

3. **「Custom Locations」タブをクリック**

4. **`/meetings`のLocationを編集**（歯車アイコン⚙️をクリック）

5. **「Custom Nginx configuration」を完全に空にする**（すべて削除）

6. **「Save」をクリック**

7. **「Details」タブに戻る**

8. **「Save」をクリック**（Proxy Host全体を保存）

9. **Proxy Hostのステータスを確認**
   - 「Online」に戻ったか確認

---

### Step 2: 基本設定を確認

Custom Nginx configurationを空欄のまま、基本設定が正しいか確認します。

#### `/meetings` Custom Locationの基本設定

| 項目 | 値 |
|------|-----|
| **Define location** | `/meetings` |
| **Scheme** | `http` |
| **Forward Hostname/IP** | `YOUR_IP_ADDRESS110/` **（末尾にスラッシュ必須）** |
| **Forward Port** | `5002` |
| **Websockets Support** | ✅ **オン（必須）** |
| **Block Common Exploits** | ✅ オン |
| **Cache Assets** | ✅ オン（オプション） |
| **Custom Nginx configuration** | **空欄のまま** |

---

### Step 3: アクセステスト（基本設定のみ）

基本設定のみでアクセスできるか確認：

1. **`https://yoshi-nas-sys.duckdns.org:8443/meetings`にアクセス**

2. **ページが表示されるか確認**（レイアウトが崩れていてもOK）

3. **ページが表示されれば、基本設定は正常に動作している**

---

### Step 4: Custom Nginx configurationを正しく追加（段階的）

基本設定が動作することを確認したら、Custom Nginx configurationを段階的に追加します。

#### 方法A: 最小限の設定（推奨）

Custom Locationの「Custom Nginx configuration」に以下を追加：

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

**重要**: `location`ブロックは使わないでください。

#### 方法B: タイムアウト設定も追加（必要に応じて）

長時間の処理でタイムアウトエラーが発生する場合：

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

---

### Step 5: 設定を保存して確認

1. **「Save」をクリック**（Custom Locationの保存）

2. **「Details」タブに戻る**

3. **「Save」をクリック**（Proxy Host全体を保存）

4. **Proxy Hostのステータスを確認**
   - 「Online」のままであることを確認
   - 「Offline」になった場合は、設定を削除してStep 1に戻る

---

## 🚨 よくある構文エラー

### エラー1: `location`ブロックをネストしている

**❌ 間違った設定**:
```nginx
location /meetings/ {
    proxy_pass http://YOUR_IP_ADDRESS110:5002;
}
```

**原因**: Custom Location内で`location`ブロックをネストすることはできません。

**✅ 正しい設定**:
```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

---

### エラー2: セミコロンが抜けている

**❌ 間違った設定**:
```nginx
proxy_set_header Host $host  # セミコロンがない
```

**✅ 正しい設定**:
```nginx
proxy_set_header Host $host;  # セミコロンが必要
```

---

### エラー3: 引用符の使い方が間違っている

**❌ 間違った設定**:
```nginx
proxy_set_header Connection "upgrade";  # 引用符が間違っている
```

**✅ 正しい設定**:
```nginx
proxy_set_header Connection "upgrade";  # ダブルクォートで囲む
```

---

## 🔍 トラブルシューティング

### Nginx設定の構文チェック

設定を追加した後、必ず構文チェックを実行：

```bash
# NASにSSH接続
ssh -p 23456 YOUR_USERNAME@YOUR_IP_ADDRESS110

# Nginx設定の構文チェック
docker exec nginx-proxy-manager nginx -t

# エラーが表示される場合は、設定を見直す
```

### Nginx Proxy Managerの再起動

設定が反映されない場合：

```bash
# Nginx Proxy Managerを再起動
docker restart nginx-proxy-manager

# ログを確認
docker logs nginx-proxy-manager --tail 50
```

---

## ✅ チェックリスト

修正後、以下を確認してください：

- [ ] Custom Nginx configurationを空欄にして、Proxy Hostが「Online」に戻ることを確認
- [ ] 基本設定（Forward Hostname/IP、Forward Port、Websockets Support）が正しいことを確認
- [ ] 基本設定のみでアクセスできることを確認
- [ ] Custom Nginx configurationを最小限の設定で追加
- [ ] 設定を保存後、Proxy Hostが「Online」のままであることを確認
- [ ] Nginx設定の構文チェックが成功することを確認
- [ ] `https://yoshi-nas-sys.duckdns.org:8443/meetings`にアクセスできることを確認

---

## 📚 参考資料

- [NGINX_PROXY_MANAGER_CUSTOM_LOCATION_OFFLINE_FIX.md](../../docs/deployment/NGINX_PROXY_MANAGER_CUSTOM_LOCATION_OFFLINE_FIX.md)
- [NGINX_PROXY_MANAGER_CUSTOM_LOCATIONS_SUMMARY.md](../../docs/deployment/NGINX_PROXY_MANAGER_CUSTOM_LOCATIONS_SUMMARY.md)

---

**作成日**: 2025-11-05  
**更新日**: 2025-11-05









