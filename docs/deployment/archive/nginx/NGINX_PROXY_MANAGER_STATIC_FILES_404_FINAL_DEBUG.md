# 🔍 静的ファイル404エラー - 最終デバッグ

**作成日**: 2025-11-02  
**目的**: 静的ファイル404エラーの根本原因を特定する

---

## ⚠️ 現在の問題

- `https://yoshi-nas-sys.duckdns.org:8443/meetings/static/css/style.css` → 404エラー
- `https://yoshi-nas-sys.duckdns.org:8443/meetings/static/js/app.js` → 404エラー
- アプリケーション側では正常: `http://192.168.68.110:5002/static/css/style.css` → 200 OK

---

## 🔍 デバッグ手順

### ステップ1: Nginx設定ファイルを確認

```bash
# NAS環境にSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# Nginx設定ファイルを確認
docker exec nginx-proxy-manager sh -c "cat /data/nginx/proxy_host/*.conf" | grep -B 10 -A 15 "meetings/static"
```

### ステップ2: locationの優先順位を確認

```bash
# locationブロックの順序を確認
docker exec nginx-proxy-manager sh -c "cat /data/nginx/proxy_host/*.conf" | grep -B 5 -A 10 "location.*meetings"
```

### ステップ3: rewriteの動作を確認

```bash
# rewriteルールを確認
docker exec nginx-proxy-manager sh -c "cat /data/nginx/proxy_host/*.conf" | grep -B 5 -A 5 "rewrite.*meetings/static"
```

### ステップ4: アクセスログで確認

```bash
# リアルタイムでアクセスログを監視
docker exec nginx-proxy-manager tail -f /data/logs/proxy-host-6_access.log | grep meetings
```

ブラウザでページをリロードして、静的ファイルへのリクエストがログに表示されるか確認してください。

### ステップ5: エラーログを確認

```bash
# エラーログを確認
docker exec nginx-proxy-manager tail -f /data/logs/proxy-host-6_error.log
```

---

## 🐛 考えられる原因と解決方法

### 原因1: locationの優先順位の問題

`location /meetings`が`location ~ ^/meetings/static/(.*)$`より先にマッチしている可能性があります。

**解決方法**: Advancedタブの設定で、`location ~ ^/meetings/static/(.*)$`を**より具体的に**記述します：

```nginx
# より具体的なlocation（^~ を使用して正規表現マッチを優先）
location ^~ /meetings/static/ {
    rewrite ^/meetings/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:5002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}
```

### 原因2: proxy_passの設定が正しくない

`proxy_pass`のURLに末尾スラッシュが必要な場合があります。

**解決方法**: `proxy_pass`のURLを修正：

```nginx
location ~ ^/meetings/static/(.*)$ {
    rewrite ^/meetings/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:5002/;  # 末尾にスラッシュを追加
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}
```

### 原因3: rewriteのbreakフラグの問題

`rewrite`の`break`フラグが正しく動作していない可能性があります。

**解決方法**: `rewrite`を`last`に変更、または`proxy_pass`のURLを修正：

```nginx
location ~ ^/meetings/static/(.*)$ {
    rewrite ^/meetings/static/(.*)$ /static/$1 last;  # breakをlastに変更
    proxy_pass http://192.168.68.110:5002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}
```

---

## 📝 チェックリスト

- [ ] Nginx設定ファイルを確認（locationブロックの順序）
- [ ] locationの優先順位を確認
- [ ] rewriteの動作を確認
- [ ] アクセスログで確認（静的ファイルへのリクエストが来ているか）
- [ ] エラーログを確認（エラーメッセージがないか）
- [ ] Advancedタブの設定を修正（locationの優先順位、proxy_passのURL）
- [ ] Nginx設定の再読み込み
- [ ] ブラウザのキャッシュをクリア
- [ ] 再度アクセスして確認

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant


