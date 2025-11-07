# 📄 document-automation サブフォルダ対応デプロイ手順

**作成日**: 2025-11-02  
**目的**: `document-automation`をサブフォルダ（`/documents`）対応にする

---

## 📋 前提条件

- ✅ ローカルでコードの変更をGitにプッシュ済み
- ✅ NAS上で`document-automation`が既にデプロイ済み

---

## 🔧 ステップ1: NAS上でコードを更新

### 1-1. NASにSSH接続

```bash
ssh AdminUser@192.168.68.110
```

### 1-2. プロジェクトディレクトリに移動

```bash
cd /home/AdminUser/nas-project/document-automation
```

### 1-3. Gitから最新のコードを取得

```bash
git pull origin feature/monitoring-fail2ban-integration
```

---

## 🔧 ステップ2: 環境変数の設定

### 2-1. `.env`ファイルに`SUBFOLDER_PATH`を追加

```bash
# .envファイルを編集
nano .env
```

以下を追加（または既存の設定に追加）:

```bash
# Subfolder Support (Nginx Proxy Manager経由で /documents でアクセスする場合)
SUBFOLDER_PATH=/documents
```

**重要**: `.env`ファイルはGit管理外のファイルです。実際の設定値はここに記述します。

---

## 🔧 ステップ3: コンテナの再ビルドと再起動

### 3-1. コンテナを停止

```bash
cd /home/AdminUser/nas-project/document-automation
sudo docker compose down
```

### 3-2. イメージを再ビルド

```bash
sudo docker compose build --no-cache web
```

### 3-3. コンテナを起動

```bash
sudo docker compose up -d
```

### 3-4. ログを確認

```bash
# コンテナのログを確認
sudo docker compose logs -f web

# 以下のログが表示されることを確認:
# - "Static files mounted at /static from ..."
# - "SUBFOLDER_PATH: /documents"
```

ログでエラーが出ていないか確認してください。

---

## 🔧 ステップ4: Nginx Proxy Managerの設定

### 4-1. Nginx Proxy ManagerのWeb UIにアクセス

ブラウザで以下にアクセス:
```
http://192.168.68.110:8181
```

### 4-2. Proxy Hostを編集

1. **「Proxy Hosts」タブをクリック**
2. **`yoshi-nas-sys.duckdns.org`をクリックして編集**

### 4-3. Advancedタブで設定を追加

1. **「Advanced」タブをクリック**
2. **「Custom Nginx Configuration」に以下を追加**（既存の設定の後に追加）:

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

3. **「Save」をクリック**
4. **Proxy Hostのステータスが「Online」のままであることを確認**

⚠️ **重要**: ステータスが「Offline」になった場合は、設定に構文エラーがある可能性があります。設定を確認してください。

---

## ✅ ステップ5: 動作確認

### 5-1. 外部アクセスでの確認

ブラウザで以下にアクセス:
```
https://yoshi-nas-sys.duckdns.org:8443/documents
```

### 5-2. ブラウザの開発者ツールで確認

1. **開発者ツールを開く**（F12キー）
2. **「Network」タブを開く**
3. **ページをリロード**（F5キー）
4. **以下が正常に読み込まれることを確認**:
   - `style.css`のステータス: **200 OK**
   - `app.js`のステータス: **200 OK**
   - `/status`エンドポイント: **200 OK**
   - APIリクエスト: **200 OK**

### 5-3. エラーがないことを確認

- **Consoleタブ**: エラーが表示されていないことを確認
- **Networkタブ**: 404エラーがないことを確認

---

## 🔍 トラブルシューティング

### 問題1: 静的ファイルが404エラーになる

**原因**: Nginx Proxy Managerの設定が正しく反映されていない

**解決方法**:
1. Nginx Proxy Managerの設定を再保存
2. Nginx設定の構文チェック:
   ```bash
   docker exec nginx-proxy-manager nginx -t
   ```
3. Nginx設定の再読み込み:
   ```bash
   docker exec nginx-proxy-manager nginx -s reload
   ```

### 問題2: `/status`エンドポイントが404エラーになる

**原因**: Nginx Proxy Managerの`/status`エンドポイントの設定が正しく反映されていない

**解決方法**:
1. Nginx Proxy ManagerのAdvancedタブの設定を確認
2. `location ~ ^/documents/status$`ブロックが正しく記述されているか確認

### 問題3: APIリクエストが404エラーになる

**原因**: JavaScriptの`apiPath()`関数が正しく動作していない

**解決方法**:
1. ブラウザのConsoleタブで`window.SUBFOLDER_PATH`の値を確認:
   ```javascript
   console.log(window.SUBFOLDER_PATH);
   ```
2. 値が`/documents`であることを確認
3. コンテナのログで`SUBFOLDER_PATH`が正しく読み込まれているか確認:
   ```bash
   sudo docker compose logs web | grep SUBFOLDER_PATH
   ```

### 問題4: コンテナが起動しない

**原因**: 環境変数の設定に問題がある可能性

**解決方法**:
1. `.env`ファイルの構文を確認（セミコロンやクォートが正しいか）
2. コンテナのログを確認:
   ```bash
   sudo docker compose logs web
   ```

---

## 📝 チェックリスト

- [ ] NAS上でGitから最新のコードを取得
- [ ] `.env`に`SUBFOLDER_PATH=/documents`を追加
- [ ] コンテナを再ビルド・再起動
- [ ] コンテナのログで`SUBFOLDER_PATH: /documents`が表示されることを確認
- [ ] Nginx Proxy ManagerのAdvancedタブに設定を追加
- [ ] Proxy Hostのステータスが「Online」のままであることを確認
- [ ] `https://yoshi-nas-sys.duckdns.org:8443/documents`にアクセスできることを確認
- [ ] 静的ファイル（CSS、JS）が正常に読み込まれることを確認
- [ ] `/status`エンドポイントが正常に動作することを確認
- [ ] APIリクエストが正常に動作することを確認

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

