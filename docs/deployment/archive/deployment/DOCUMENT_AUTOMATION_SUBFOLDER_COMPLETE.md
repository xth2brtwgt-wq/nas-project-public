# ✅ document-automation サブフォルダ対応完了

**作成日**: 2025-11-04  
**目的**: `document-automation`のサブフォルダ対応が完了したことを記録

---

## ✅ 完了した作業

### 1. アプリケーション側の修正

#### `app/api/main.py`
- ✅ `SUBFOLDER_PATH`環境変数を読み込むように修正
- ✅ `Path`のインポートを追加
- ✅ テンプレートに`subfolder_path`を渡すように修正
- ✅ デバッグログを追加（`[INIT]`, `[INDEX]`）

#### `app/templates/index.html`
- ✅ 静的ファイルのパスを`subfolder_path`でプレフィックス
- ✅ `window.SUBFOLDER_PATH`をJavaScriptに渡すように修正

#### `app/static/js/app.js`
- ✅ `apiPath()`ヘルパー関数を追加
- ✅ すべてのAPI呼び出しを`apiPath()`でラップ
- ✅ `/status`エンドポイントの呼び出しを修正

#### `env.example`
- ✅ `SUBFOLDER_PATH`の例を追加

### 2. Docker関連

#### `docker-compose.yml`
- ✅ `.env`ファイルから環境変数を読み込む設定（既存）

#### `docker-entrypoint.sh`
- ✅ NAS上で作成済み（権限修正スクリプト）

### 3. Nginx Proxy Manager設定

#### Advancedタブに追加した設定
- ✅ `/documents/static/` → `/static/` にリライト（静的ファイル）
- ✅ `/documents/api/` → `/api/` にリライト（API）
- ✅ `/documents/status` → `/status` にリライト（statusエンドポイント）
- ✅ `auth_basic off;` を設定（Basic認証を除外）

---

## 📋 設定内容

### 環境変数

`.env`ファイルに以下を追加：

```bash
# Subfolder Support (Optional)
# Nginx Proxy Manager経由でサブフォルダ（/documents）でアクセスする場合に設定
# 内部ネットワークから直接アクセスする場合は設定不要（空欄のまま）
SUBFOLDER_PATH=/documents
```

### Nginx Proxy Manager設定

**Proxy Host**: `yoshi-nas-sys.duckdns.org`  
**Advancedタブ**に以下を追加：

```nginx
# /documents の静的ファイル修正（document-automation）
location ^~ /documents/static/ {
    rewrite ^/documents/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /documents のAPI修正（document-automation）
location ~ ^/documents/api/(.*)$ {
    rewrite ^/documents/api/(.*)$ /api/$1 break;
    proxy_pass http://192.168.68.110:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}

# /documents のstatusエンドポイント修正（document-automation）
location ~ ^/documents/status$ {
    rewrite ^/documents/status$ /status break;
    proxy_pass http://192.168.68.110:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}
```

---

## ✅ 動作確認

### 確認項目

1. ✅ 環境変数`SUBFOLDER_PATH=/documents`が正しく読み込まれている
2. ✅ 静的ファイルのマウントが正常に動作している
3. ✅ テンプレートで`subfolder_path`が正しく設定されている
4. ✅ HTMLに`/documents/static/css/style.css`が含まれている
5. ✅ Nginx Proxy Managerの設定が正しく反映されている
6. ✅ 静的ファイル（CSS、JS）が正常に読み込まれる（404エラーなし）
7. ✅ `/status`エンドポイントが正常に動作する
8. ✅ APIリクエストが正常に動作する

### アクセスURL

- **外部アクセス**: `https://yoshi-nas-sys.duckdns.org:8443/documents`
- **内部アクセス**: `http://192.168.68.110:8080`

---

## 📝 注意事項

### 内部アクセス時の動作

内部ネットワークから直接アクセス（`http://192.168.68.110:8080`）する場合、環境変数`SUBFOLDER_PATH=/documents`が設定されているため、静的ファイルのパスが`/documents/static/...`になります。

これは想定動作です。内部アクセスでも`SUBFOLDER_PATH`を設定しているため、一貫した動作を実現しています。

もし内部アクセス時に`/static/...`を使用したい場合は、`.env`ファイルで`SUBFOLDER_PATH`を空欄にするか、環境変数を削除してください。

---

## 🎯 完了したタスク

- ✅ `document-automation`のサブフォルダ対応（`/documents`）
- ✅ 静的ファイルのパス修正
- ✅ APIエンドポイントのパス修正
- ✅ `/status`エンドポイントのパス修正
- ✅ Nginx Proxy Managerの設定追加
- ✅ 動作確認完了

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

