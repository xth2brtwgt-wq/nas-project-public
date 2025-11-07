# 🔍 Nginx Proxy Manager - 静的ファイル直接アクセステスト

**作成日**: 2025-11-02  
**目的**: 静的ファイルへのリクエストが正しく処理されているか直接確認する方法

---

## 🔍 直接アクセステスト

### ステップ1: アプリケーションに直接アクセス

```bash
# アプリケーションに直接アクセスして静的ファイルを確認
curl -I http://192.168.68.110:5002/static/css/style.css
```

**期待される結果**: HTTP 200 OK

### ステップ2: Nginx経由でアクセス

```bash
# Nginx経由でアクセスして静的ファイルを確認
curl -I https://yoshi-nas-sys.duckdns.org:8443/meetings/static/css/style.css
```

**期待される結果**: HTTP 200 OK

もし404エラーが出る場合、Nginxの設定が正しく動作していない可能性があります。

### ステップ3: 詳細なレスポンスを確認

```bash
# 詳細なレスポンスを確認
curl -v https://yoshi-nas-sys.duckdns.org:8443/meetings/static/css/style.css 2>&1 | head -20
```

---

## 🐛 トラブルシューティング

### 404エラーが出る場合

#### 1. locationの優先順位を確認

```bash
# locationの順序を確認
docker exec nginx-proxy-manager sh -c "cat /data/nginx/proxy_host/*.conf" | grep -B 5 -A 10 "location.*meetings"
```

#### 2. rewriteの動作を確認

```bash
# rewriteが正しく動作しているか確認
curl -v https://yoshi-nas-sys.duckdns.org:8443/meetings/static/css/style.css 2>&1 | grep -E "(HTTP|Location|rewrite)"
```

#### 3. proxy_passの設定を確認

```bash
# proxy_passの設定を確認
docker exec nginx-proxy-manager sh -c "cat /data/nginx/proxy_host/*.conf" | grep -B 5 -A 5 "proxy_pass.*5002"
```

### 403エラーが出る場合

Basic認証の設定が静的ファイルにも適用されている可能性があります。

#### 解決方法: 静的ファイルのlocationブロックから認証を除外

Advancedタブの「Custom Nginx Configuration」を修正：

```nginx
# /meetings の静的ファイル修正（認証を除外）
location ~ ^/meetings/static/(.*)$ {
    rewrite ^/meetings/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:5002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    # Basic認証を除外（静的ファイルは認証不要）
    # auth_basic off;
}
```

---

## 📝 チェックリスト

- [ ] アプリケーションに直接アクセス（curl）
- [ ] Nginx経由でアクセス（curl）
- [ ] ステータスコードを確認（200 OKか404か）
- [ ] 詳細なレスポンスを確認
- [ ] locationの優先順位を確認
- [ ] rewriteの動作を確認

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant


