# 🔍 Nginx Proxy Manager - 静的ファイルリクエストのデバッグ

**作成日**: 2025-11-02  
**目的**: 静的ファイルへのリクエストが正しく処理されているか確認する方法

---

## ✅ 確認結果

### Nginx設定の再読み込み
- ✅ Nginx設定の構文チェック: 成功
- ✅ Nginx設定の再読み込み: 成功

### アクセスログの確認
- ✅ `/meetings`へのアクセス: 200 OK
- ❓ 静的ファイルへのリクエストログが見当たらない

---

## 🔍 静的ファイルリクエストの確認

### ステップ1: リアルタイムでアクセスログを監視

```bash
# アクセスログをリアルタイムで監視
docker exec nginx-proxy-manager tail -f /data/logs/proxy-host-6_access.log | grep -E "(meetings|static)"
```

### ステップ2: ブラウザでページをリロード

1. **ブラウザの開発者ツールを開く**（F12キー）
2. **「Network」タブを開く**
3. **「Disable cache」にチェックを入れる**
4. **`https://yoshi-nas-sys.duckdns.org:8443/meetings`にアクセス**
5. **ページをリロード**（`Cmd+Shift+R`または`Ctrl+Shift+R`）

### ステップ3: アクセスログで確認

リアルタイムでアクセスログを監視している場合、以下のようなログが表示されるはずです：

```
[04/Nov/2025:10:XX:XX +0900] - 200 200 - GET https yoshi-nas-sys.duckdns.org "/meetings/static/css/style.css" ...
[04/Nov/2025:10:XX:XX +0900] - 200 200 - GET https yoshi-nas-sys.duckdns.org "/meetings/static/js/app.js" ...
```

または、404エラーの場合：

```
[04/Nov/2025:10:XX:XX +0900] - 404 404 - GET https yoshi-nas-sys.duckdns.org "/meetings/static/css/style.css" ...
```

### ステップ4: 直接アクセステスト

```bash
# アプリケーションに直接アクセスして静的ファイルを確認
curl -I http://192.168.68.110:5002/static/css/style.css

# Nginx経由でアクセスして静的ファイルを確認
curl -I https://yoshi-nas-sys.duckdns.org:8443/meetings/static/css/style.css
```

---

## 🐛 トラブルシューティング

### 静的ファイルへのリクエストが404エラーの場合

#### 1. locationの優先順位を確認

Nginxの設定ファイルを確認：

```bash
docker exec nginx-proxy-manager sh -c "cat /data/nginx/proxy_host/*.conf" | grep -B 10 -A 10 "location.*meetings"
```

#### 2. locationの順序を確認

正しい順序：
1. `location ~ ^/meetings/static/(.*)$` - 正規表現マッチ（先に記述）
2. `location /meetings` - 通常のパス（後に記述）

#### 3. rewriteの動作を確認

```bash
# rewriteが正しく動作しているか確認
curl -v https://yoshi-nas-sys.duckdns.org:8443/meetings/static/css/style.css 2>&1 | grep -E "(HTTP|Location|rewrite)"
```

#### 4. proxy_passの設定を確認

```bash
# proxy_passの設定を確認
docker exec nginx-proxy-manager sh -c "cat /data/nginx/proxy_host/*.conf" | grep -B 5 -A 5 "proxy_pass.*5002"
```

### 静的ファイルへのリクエストがログに表示されない場合

1. **ブラウザの開発者ツール → Networkタブ**
   - 静的ファイルが実際にリクエストされているか確認
   - リクエストURLを確認
   - ステータスコードを確認

2. **Nginxのエラーログを確認**:

```bash
docker exec nginx-proxy-manager tail -f /data/logs/proxy-host-6_error.log
```

3. **アプリケーション側のログを確認**:

```bash
docker logs meeting-minutes-byc --tail 100 -f
```

---

## 📝 チェックリスト

- [ ] リアルタイムでアクセスログを監視
- [ ] ブラウザでページをリロード
- [ ] 静的ファイルへのリクエストがログに表示されるか確認
- [ ] 静的ファイルのステータスコードを確認（200 OKか404か）
- [ ] 直接アクセステスト（curl）
- [ ] locationの優先順位を確認
- [ ] rewriteの動作を確認

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant
