# 📋 サブフォルダ対応状況まとめ

**作成日**: 2025-11-02  
**目的**: 各サービスのサブフォルダ対応状況をまとめる

---

## ✅ 対応完了

### meeting-minutes-byc (`/meetings`)

- ✅ **対応完了**
- ✅ Flask `APPLICATION_ROOT`設定
- ✅ 静的ファイルのパス修正（テンプレート側で手動追加）
- ✅ Socket.IOとAPIエンドポイントのパス修正
- ✅ Nginx Proxy ManagerのAdvancedタブで静的ファイル・API・Socket.IOのリライト設定

### amazon-analytics (`/analytics`)

- ✅ **対応完了**
- ✅ FastAPIアプリケーション（`root_path`は設定しない）
- ✅ 静的ファイルのパス修正（テンプレート側で手動追加）
- ✅ APIエンドポイントのパス修正（JavaScript側）
- ✅ Nginx Proxy ManagerのAdvancedタブで静的ファイル・APIのリライト設定

### nas-dashboard-monitoring (`/monitoring`)

- ✅ **対応完了**
- ✅ Reactアプリケーション（`homepage: "/monitoring"`設定）
- ✅ FastAPIバックエンド
- ✅ 静的ファイルのパス修正
- ✅ APIエンドポイントのパス修正（TypeScript側）
- ✅ WebSocket接続のパス修正
- ✅ Nginx Proxy ManagerのAdvancedタブで静的ファイル・API・WebSocketのリライト設定

### document-automation (`/documents`)

- ✅ **対応完了**
- ✅ FastAPIアプリケーション（`root_path`は設定しない）
- ✅ 静的ファイルのパス修正（テンプレート側で手動追加）
- ✅ APIエンドポイントのパス修正（JavaScript側）
- ✅ `/status`エンドポイントのパス修正
- ✅ Nginx Proxy ManagerのAdvancedタブで静的ファイル・API・statusエンドポイントのリライト設定

---

## 📝 確認手順（すべて対応完了）

**現状**:
- FastAPIアプリケーション
- 静的ファイルを`/static/...`で参照
- テンプレートで`/static/css/style.css`、`/static/js/app.js`を使用

**対応が必要な可能性**:
- サブフォルダ（`/analytics`）経由でアクセスする場合、静的ファイルのパスが正しく解決されない可能性
- FastAPIでサブフォルダ対応するには、`root_path`パラメータを使用する必要がある

**対応方法**:
```python
# app/api/main.py
app = FastAPI(
    title=settings.APP_NAME,
    version=__version__,
    description="Amazon購入履歴分析システム",
    root_path="/analytics"  # サブフォルダパスを設定
)
```

**テンプレート側の修正**:
```html
<!-- 静的ファイルのパスを修正 -->
<link rel="stylesheet" href="{{ '/analytics' if request.url.path.startswith('/analytics') else '' }}/static/css/style.css">
```

**または、Nginx Proxy ManagerのAdvancedタブでリライト設定**:
```nginx
# /analytics の静的ファイル修正
location ^~ /analytics/static/ {
    rewrite ^/analytics/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:8001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}
```

---

### nas-dashboard-monitoring (`/monitoring`)

**現状**:
- Reactアプリケーション（フロントエンド）
- FastAPI（バックエンド）
- `REACT_APP_API_URL=http://192.168.68.110:8002`でバックエンドのURLを指定
- `%PUBLIC_URL%`を使用しているが、`package.json`に`homepage`設定がない

**対応が必要な可能性**:
- サブフォルダ（`/monitoring`）経由でアクセスする場合、以下が必要：
  1. Reactアプリのベースパス設定
  2. バックエンドのAPI URLの調整
  3. 静的ファイルのパス調整

**対応方法**:

#### 1. `package.json`に`homepage`を追加
```json
{
  "name": "nas-dashboard-monitoring-frontend",
  "version": "1.0.0",
  "homepage": "/monitoring",  // 追加
  ...
}
```

#### 2. ビルド時に`PUBLIC_URL`を設定
```bash
PUBLIC_URL=/monitoring npm run build
```

#### 3. バックエンドのAPI URLの調整
- 相対パスで`/api/...`を使用するか、`/monitoring/api/...`に変更
- または、環境変数で制御：
  ```bash
  REACT_APP_API_URL=/monitoring/api
  ```

#### 4. Nginx Proxy ManagerのAdvancedタブでリライト設定
```nginx
# /monitoring のAPI修正
location ~ ^/monitoring/api/(.*)$ {
    rewrite ^/monitoring/api/(.*)$ /api/$1 break;
    proxy_pass http://192.168.68.110:8002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

---

## 📝 確認手順

### meeting-minutes-byc の確認

1. **`https://yoshi-nas-sys.duckdns.org:8443/meetings`にアクセス**
2. **ブラウザの開発者ツールで確認**:
   - CSSファイルが正しく読み込まれているか（404エラーが出ていないか）
   - JavaScriptファイルが正しく読み込まれているか
   - Socket.IO接続が正常に確立されているか
   - APIリクエストが正しく送信されているか
   - レイアウトが正しく表示されているか

### amazon-analytics の確認

1. **`https://yoshi-nas-sys.duckdns.org:8443/analytics`にアクセス**
2. **ブラウザの開発者ツールで確認**:
   - CSSファイルが正しく読み込まれているか（404エラーが出ていないか）
   - JavaScriptファイルが正しく読み込まれているか
   - APIリクエストが正しく送信されているか
   - レイアウトが正しく表示されているか

### nas-dashboard-monitoring の確認

1. **`https://yoshi-nas-sys.duckdns.org:8443/monitoring`にアクセス**
2. **ブラウザの開発者ツールで確認**:
   - 静的ファイル（CSS、JS、画像）が正しく読み込まれているか
   - APIリクエストが正しく送信されているか（404エラーが出ていないか）
   - WebSocket接続が正常に確立されているか
   - レイアウトが正しく表示されているか

### document-automation の確認

1. **`https://yoshi-nas-sys.duckdns.org:8443/documents`にアクセス**
2. **ブラウザの開発者ツールで確認**:
   - CSSファイルが正しく読み込まれているか（404エラーが出ていないか）
   - JavaScriptファイルが正しく読み込まれているか
   - `/status`エンドポイントが正しく動作しているか
   - APIリクエストが正しく送信されているか
   - レイアウトが正しく表示されているか

---

## ✅ 完了状況

すべてのサービスのサブフォルダ対応が完了しました：

- ✅ meeting-minutes-byc (`/meetings`)
- ✅ amazon-analytics (`/analytics`)
- ✅ nas-dashboard-monitoring (`/monitoring`)
- ✅ document-automation (`/documents`)
- ✅ youtube-to-notion (`/youtube`)

---

## 📚 参考資料

- [meeting-minutes-byc サブフォルダ対応完了](MEETING_MINUTES_SUBFOLDER_DEPLOY_COMPLETE.md)
- [FastAPI root_path](https://fastapi.tiangolo.com/advanced/behind-a-proxy/#root_path)
- [React Create React App - デプロイメント](https://create-react-app.dev/docs/deployment/#building-for-relative-paths)

---

---

## 📚 参考資料

- [meeting-minutes-byc サブフォルダ対応完了](MEETING_MINUTES_SUBFOLDER_DEPLOY_COMPLETE.md)
- [amazon-analytics サブフォルダ対応完了](AMAZON_ANALYTICS_SUBFOLDER_PATH_VERIFICATION.md)
- [nas-dashboard-monitoring サブフォルダ対応完了](SUBFOLDER_SUPPORT_COMPLETE.md)
- [document-automation サブフォルダ対応完了](DOCUMENT_AUTOMATION_SUBFOLDER_DEPLOY.md)
- [Nginx Proxy Manager Advancedタブ完全設定](NGINX_PROXY_MANAGER_ADVANCED_TAB_COMPLETE_CONFIG.md)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

