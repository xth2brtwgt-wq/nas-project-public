# 🔄 Nginx Proxy Manager - 設定再読み込みと確認

**作成日**: 2025-11-02  
**目的**: 設定が正しく反映されているのに404エラーが出る場合の対処法

---

## ✅ 確認結果

設定ファイルを確認した結果、**設定は正しく反映されています**：

```nginx
# Advancedタブの設定（Custom Locationより前に記述）
location ~ ^/meetings/static/(.*)$ {
    rewrite ^/meetings/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:5002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# Custom Locationの設定（後ろに記述）
location /meetings {
    proxy_pass http://192.168.68.110:5002/;
    ...
}
```

---

## 🔄 設定が反映されない場合の対処法

### ステップ1: Nginx設定の構文チェック

```bash
docker exec nginx-proxy-manager nginx -t
```

**期待される出力**:
```
nginx: the configuration file /etc/nginx/nginx.conf test is successful
```

### ステップ2: Nginx設定の再読み込み

```bash
docker exec nginx-proxy-manager nginx -s reload
```

または、Nginx Proxy Managerを再起動：

```bash
docker restart nginx-proxy-manager
```

### ステップ3: ブラウザキャッシュのクリア

1. **ブラウザの開発者ツールを開く**（F12キー）
2. **「Network」タブを開く**
3. **「Disable cache」にチェックを入れる**
4. **ページをリロード**（`Cmd+Shift+R`または`Ctrl+Shift+R`）

### ステップ4: アクセステスト

1. **`https://yoshi-nas-sys.duckdns.org:8443/meetings`にアクセス**

2. **ブラウザの開発者ツール → Networkタブ**
   - `style.css`のリクエストURL: `https://yoshi-nas-sys.duckdns.org:8443/meetings/static/css/style.css`
   - ステータスコード: **200 OK**（404ではない）
   - `app.js`のリクエストURL: `https://yoshi-nas-sys.duckdns.org:8443/meetings/static/js/app.js`
   - ステータスコード: **200 OK**（404ではない）

---

## 🐛 トラブルシューティング

### まだ404エラーが出る場合

#### 1. Nginxログを確認

```bash
# エラーログを確認
docker exec nginx-proxy-manager tail -f /data/logs/proxy-host-6_error.log

# アクセスログを確認
docker exec nginx-proxy-manager tail -f /data/logs/proxy-host-6_access.log | grep meetings
```

#### 2. アプリケーション側のログを確認

```bash
docker logs meeting-minutes-byc --tail 100
```

#### 3. 直接アクセステスト

```bash
# アプリケーションに直接アクセスして静的ファイルを確認
curl -I http://192.168.68.110:5002/static/css/style.css
```

#### 4. locationの優先順位を確認

Nginxの`location`の優先順位：
1. `=` - 完全一致
2. `^~` - 前方一致（正規表現マッチを無効化）
3. `~` / `~*` - 正規表現マッチ
4. 通常のパス（前方一致）

現在の設定では、`location ~ ^/meetings/static/(.*)$`（正規表現マッチ）が`location /meetings`（通常のパス）より優先されるはずです。

もし問題がある場合は、より具体的な`location`を使用：

```nginx
# より具体的なlocation（= を使用）
location = /meetings/static/css/style.css {
    rewrite ^/meetings/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:5002;
    ...
}

# または、^~ を使用（正規表現マッチを無効化）
location ^~ /meetings/static/ {
    rewrite ^/meetings/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:5002;
    ...
}
```

---

## 📝 チェックリスト

- [ ] Nginx設定の構文チェック（`nginx -t`）
- [ ] Nginx設定の再読み込み（`nginx -s reload`）
- [ ] ブラウザのキャッシュをクリア
- [ ] `/meetings`でアクセスしてCSS/JSが正しく読み込まれることを確認
- [ ] 404エラーが出ていないか確認
- [ ] CSSが正しく適用されているか確認
- [ ] Nginxログを確認（エラーがないか確認）

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant


