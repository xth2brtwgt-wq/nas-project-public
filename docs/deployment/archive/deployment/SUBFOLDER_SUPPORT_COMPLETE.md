# ✅ サブフォルダ対応完了

**作成日**: 2025-11-02  
**更新日**: 2025-11-04  
**目的**: すべてのサービスのサブフォルダ対応が完了したことを記録

---

## ✅ 対応完了したサービス

### 1. meeting-minutes-byc (`/meetings`)

**対応完了日**: 2025-11-02

- ✅ Flask `APPLICATION_ROOT`設定
- ✅ 静的ファイルのパス修正（テンプレート側で手動追加）
- ✅ Socket.IOとAPIエンドポイントのパス修正
- ✅ Nginx Proxy ManagerのAdvancedタブで静的ファイル・API・Socket.IOのリライト設定

**アクセスURL**: `https://yoshi-nas-sys.duckdns.org:8443/meetings`

---

### 2. amazon-analytics (`/analytics`)

**対応完了日**: 2025-11-04

- ✅ FastAPIアプリケーションの修正
- ✅ 静的ファイルのパス修正（テンプレート側で`subfolder_path`を使用）
- ✅ APIエンドポイントのパス修正（JavaScript側で`apiPath`ヘルパー関数を使用）
- ✅ Nginx Proxy ManagerのAdvancedタブで静的ファイル・APIのリライト設定
- ✅ `root_path`を削除して静的ファイルのパスを修正

**アクセスURL**: `https://yoshi-nas-sys.duckdns.org:8443/analytics`

**修正内容**:
- FastAPIの`root_path`を削除（静的ファイルのパスに影響するため）
- 静的ファイルは`/static/...`でマウント
- Nginx側で`/analytics/static/...`を`/static/...`にリライト

---

### 3. nas-dashboard-monitoring (`/monitoring`)

**対応完了日**: 2025-11-04

- ✅ Reactアプリケーションの`homepage`設定
- ✅ Dockerfileで`PUBLIC_URL`環境変数を設定
- ✅ APIとWebSocketのパス修正（JavaScript側で`basePath`を使用）
- ✅ Nginx Proxy ManagerのAdvancedタブで静的ファイル・API・WebSocketのリライト設定

**アクセスURL**: `https://yoshi-nas-sys.duckdns.org:8443/monitoring`

**修正内容**:
- `package.json`に`homepage: "/monitoring"`を追加
- Dockerfileで`PUBLIC_URL`環境変数を設定
- Reactアプリ側で`getBasePath()`関数でサブフォルダパスを自動検出
- APIとWebSocketのパスを`basePath`を使用するように修正

---

## 📋 Nginx Proxy Managerの設定

### Advancedタブの完全な設定

すべてのサービスの静的ファイル・API・WebSocket設定をNginx Proxy ManagerのAdvancedタブに追加しました。

詳細は`docs/deployment/NGINX_PROXY_MANAGER_ADVANCED_TAB_COMPLETE_CONFIG.md`を参照してください。

---

## 🔍 動作確認

### meeting-minutes-byc

- ✅ 静的ファイルが正しく読み込まれる
- ✅ Socket.IO接続が正常に確立される
- ✅ APIリクエストが正常に動作する

### amazon-analytics

- ✅ 静的ファイルが正しく読み込まれる（`style.css`、`app.js`）
- ✅ APIリクエストが正常に動作する
- ✅ 画面が正しく表示される

### nas-dashboard-monitoring

- ✅ 静的ファイルが正しく読み込まれる（`main.*.css`、`main.*.js`）
- ✅ `manifest.json`が正しく読み込まれる
- ✅ APIリクエストが正常に動作する
- ✅ WebSocket接続が正常に確立される

---

## 📝 環境変数の設定

### meeting-minutes-byc

`.env`ファイル:
```bash
SUBFOLDER_PATH=/meetings
```

### amazon-analytics

`.env`ファイル:
```bash
SUBFOLDER_PATH=/analytics
```

### nas-dashboard-monitoring

`.env`ファイル（オプション）:
```bash
PUBLIC_URL=/monitoring
```

---

## 🎉 完了

すべての主要サービスのサブフォルダ対応が完了しました！

- ✅ meeting-minutes-byc (`/meetings`)
- ✅ amazon-analytics (`/analytics`)
- ✅ nas-dashboard-monitoring (`/monitoring`)

すべてのサービスが`https://yoshi-nas-sys.duckdns.org:8443`経由でアクセス可能になりました。

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

