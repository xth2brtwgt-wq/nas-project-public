# ✅ 外部アクセス時の404エラー確認

**作成日**: 2025-11-04  
**目的**: 外部アクセス時に404エラーが発生する問題を確認

---

## ❌ 問題

外部からアクセスすると、HTTP 404が返ってきます：

```bash
curl -v https://yoshi-nas-sys.duckdns.org:8443/analytics/
< HTTP/2 404 
< {"detail":"Not Found"}
```

---

## 🔍 確認手順

### ステップ1: 末尾スラッシュなしでアクセス

```bash
# 末尾スラッシュなしでアクセス
curl -v https://yoshi-nas-sys.duckdns.org:8443/analytics
```

### ステップ2: ログを確認

```bash
cd ~/nas-project/amazon-analytics

# アクセスログを確認
sudo docker compose logs web --tail 50 | grep -i "GET\|POST\|404\|analytics"

# 認証関連のログを確認
sudo docker compose logs web | grep -i "\[AUTH\]" | tail -20
```

### ステップ3: Nginx Proxy ManagerのCustom Location設定を確認

Custom Location設定で`/analytics`が正しく設定されているか確認：

- **Define location**: `/analytics`（末尾スラッシュなし）
- **Forward Hostname/IP**: `192.168.68.110`
- **Forward Port**: `8001`

### ステップ4: Advancedタブの設定を確認

Advancedタブで`/analytics`に関する設定が正しく追加されているか確認：

```nginx
# /analytics の静的ファイル修正
location ^~ /analytics/static/ {
    rewrite ^/analytics/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:8001;
    ...
}

# /analytics のAPI修正
location ~ ^/analytics/api/(.*)$ {
    rewrite ^/analytics/api/(.*)$ /api/$1 break;
    proxy_pass http://192.168.68.110:8001;
    ...
}
```

---

## 🔧 トラブルシューティング

### 404エラーが続く場合

1. **Custom Location設定を確認**:
   - `/analytics`が正しく設定されているか
   - Forward Hostname/IPとForward Portが正しいか

2. **アプリケーション側のルート設定を確認**:
   ```bash
   # アプリケーションのルートエンドポイントを確認
   curl http://192.168.68.110:8001/
   ```

3. **リクエストがアプリケーションに到達しているか確認**:
   ```bash
   # アクセスログを確認
   sudo docker compose logs web --tail 100
   ```

### 末尾スラッシュの処理

Nginx Proxy ManagerのCustom Location設定では、`/analytics`と`/analytics/`の両方に対応する必要があります。

Advancedタブに以下の設定を追加：

```nginx
# /analytics のルートパス修正（末尾スラッシュあり）
location = /analytics/ {
    rewrite ^/analytics/$ / break;
    proxy_pass http://192.168.68.110:8001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
}
```

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

