# 🔒 Nginx CSP設定でCDNを許可する方法

**作成日**: 2025-01-27  
**対象**: Nginx Proxy ManagerでCSPを設定している環境

---

## 📋 問題

Content Security Policy (CSP) によって、外部CDNからのCSSやJavaScriptファイルがブロックされ、以下のエラーが発生します：

```
Refused to load https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css 
because it does not appear in the style-src directive of the Content Security Policy.

Refused to load https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css 
because it does not appear in the style-src directive of the Content Security Policy.

Refused to load https://cdn.socket.io/4.7.2/socket.io.min.js 
because it does not appear in the script-src directive of the Content Security Policy.
```

---

## 🔍 原因

現在のCSP設定では、外部CDNドメインが許可されていないため、以下のCDNからのリソースが読み込めません：

- `https://cdn.jsdelivr.net` - Bootstrap CSS、Bootstrap Icons、Bootstrap JS
- `https://cdnjs.cloudflare.com` - Font Awesome、Socket.IO
- `https://cdn.socket.io` - Socket.IO（一部のアプリで使用）

---

## ✅ 解決方法

CSP設定を更新して、必要なCDNドメインを許可します。

### 修正前のCSP設定

```nginx
# Content Security Policy
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' wss: ws:;" always;
```

### 修正後のCSP設定

```nginx
# Content Security Policy（CDNを許可）
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://cdn.socket.io; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; img-src 'self' data: https:; font-src 'self' data: https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; connect-src 'self' wss: ws: http: https:; form-action 'self'; frame-ancestors 'self';" always;
```

---

## 🔧 設定手順

### ステップ1: Nginx Proxy Managerにアクセス

1. **Nginx Proxy ManagerのWeb UIにアクセス**
   - `http://192.168.68.110:8181`

2. **Proxy Hosts → yoshi-nas-sys.duckdns.org → Advanced → Custom Nginx Configuration**

### ステップ2: CSP設定を更新

1. **既存のCSP設定を検索**
   - `Content-Security-Policy`で検索

2. **CSP設定を修正後の設定に置き換え**

3. **「Save」をクリック**

### ステップ3: 設定を確認

1. **Proxy Hostのステータスを確認**
   - 「Online」になっていることを確認

2. **ブラウザの開発者ツールで確認**
   - コンソールエラーが解消されていることを確認
   - CSSが正しく適用されていることを確認

---

## 📝 変更内容の詳細

### 追加したCDNドメイン

#### script-src（JavaScript）
- `https://cdn.jsdelivr.net` - Bootstrap JS
- `https://cdnjs.cloudflare.com` - Socket.IO
- `https://cdn.socket.io` - Socket.IO（一部のアプリで使用）

#### style-src（CSS）
- `https://cdn.jsdelivr.net` - Bootstrap CSS、Bootstrap Icons
- `https://cdnjs.cloudflare.com` - Font Awesome

#### font-src（フォント）
- `https://cdn.jsdelivr.net` - Bootstrap Iconsのフォント
- `https://cdnjs.cloudflare.com` - Font Awesomeのフォント

### 追加したディレクティブ

- `form-action 'self'` - フォーム送信を同一オリジンのみに制限
- `frame-ancestors 'self'` - iframe内での表示を同一オリジンのみに制限
- `connect-src`に`http: https:`を追加 - APIリクエストを許可

---

## ✅ 確認方法

### 1. ブラウザの開発者ツールで確認

1. **ブラウザの開発者ツールを開く**
   - F12キーを押す
   - または、右クリック → 「検証」

2. **Consoleタブを確認**
   - CSPエラーが表示されていないことを確認

3. **Networkタブを確認**
   - CSSファイル（`bootstrap.min.css`、`all.min.css`など）が正常に読み込まれていることを確認
   - JavaScriptファイル（`socket.io.min.js`、`bootstrap.bundle.min.js`など）が正常に読み込まれていることを確認

### 2. 画面の表示を確認

1. **各サービスにアクセス**
   - `/analytics`
   - `/monitoring`
   - `/meetings`
   - `/documents`
   - `/youtube`

2. **CSSが正しく適用されていることを確認**
   - Bootstrapのスタイルが適用されている
   - Font Awesomeのアイコンが表示されている
   - レイアウトが正しく表示されている

---

## 🔒 セキュリティに関する注意事項

### CDNの信頼性

許可しているCDNドメインは、以下の信頼できるCDNプロバイダーです：

- **jsDelivr**: オープンソースのCDNプロバイダー、GitHub、npm、WordPressと統合
- **Cloudflare CDN**: 大手CDNプロバイダー、セキュリティ機能が充実
- **Socket.IO CDN**: Socket.IO公式CDN

### セキュリティベストプラクティス

1. **特定のバージョンを指定**
   - アプリケーション側で、CDNのURLに特定のバージョンを指定（例: `bootstrap@5.3.0`）
   - これにより、予期しないバージョンアップを防ぐ

2. **Subresource Integrity (SRI) の使用**
   - 可能であれば、SRIハッシュを使用してCDNリソースの整合性を検証
   - ただし、現在のアプリケーションでは実装されていないため、信頼できるCDNを使用

3. **定期的な監視**
   - ブラウザの開発者ツールで、予期しないリソースの読み込みがないか確認

---

## 📚 関連ドキュメント

- [NGINX_FINAL_CONFIG.md](NGINX_FINAL_CONFIG.md) - 完全なNginx設定
- [NGINX_SECURITY_HEADERS_WITHOUT_RATE_LIMIT.md](NGINX_SECURITY_HEADERS_WITHOUT_RATE_LIMIT.md) - セキュリティヘッダーの設定方法

---

## 🐛 トラブルシューティング

### CSPエラーが解消されない場合

1. **ブラウザのキャッシュをクリア**
   - Ctrl+Shift+Delete（Windows/Linux）
   - Cmd+Shift+Delete（Mac）

2. **Nginx設定の構文を確認**
   ```bash
   docker exec nginx-proxy-manager nginx -t
   ```

3. **Nginx Proxy Managerを再起動**
   ```bash
   docker restart nginx-proxy-manager
   ```

### 特定のCDNリソースが読み込めない場合

1. **ブラウザの開発者ツールで確認**
   - Networkタブで、読み込めないリソースのURLを確認
   - そのURLが許可されているCDNドメインに含まれているか確認

2. **CSP設定を確認**
   - 必要なCDNドメインが`script-src`、`style-src`、`font-src`に含まれているか確認

---

## ✅ 完了

CSP設定を更新することで、外部CDNからのCSSやJavaScriptファイルが正常に読み込まれ、CSSが正しく適用されるようになります。

