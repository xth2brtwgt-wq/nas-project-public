# 🔍 静的ファイル404エラー - 詳細トラブルシューティング

**作成日**: 2025-11-02  
**目的**: `/meetings/static/...`で404エラーが発生する問題の詳細な原因特定と解決

---

## ⚠️ 現在の状況

- `style.css`と`app.js`が赤色表示（404エラー）
- ブラウザは`/meetings/static/css/style.css`をリクエストしている
- アプリケーション側では`static_url_path=/meetings/static`を設定済み

---

## 🔍 原因の特定

### 問題の流れ

1. **Flask側**: `static_url_path=/meetings/static`により、`url_for('static', ...)`が`/meetings/static/css/style.css`を生成
2. **ブラウザ**: `https://yoshi-nas-sys.duckdns.org:8443/meetings/static/css/style.css`をリクエスト
3. **Nginx Proxy Manager**: Custom Location（`/meetings`）が`/meetings`へのアクセスを`http://192.168.68.110:5002/`に転送
4. **問題**: `/meetings/static/css/style.css`へのリクエストが`http://192.168.68.110:5002/meetings/static/css/style.css`に転送される
5. **Flask側**: `/meetings/static/css/style.css`というパスは存在しない（実際のパスは`/static/css/style.css`）
6. **結果**: 404エラー

---

## ✅ 解決方法の選択

### オプション1: Nginx側でリライト（推奨・確実）

**Advancedタブでリライトルールを追加**（Custom Locationより**前に**記述）：

```nginx
# /meetings の静的ファイル修正（最重要: 他のlocationより前に記述）
location ~ ^/meetings/static/(.*)$ {
    rewrite ^/meetings/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:5002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**注意**: `location`ブロックは**Custom Locationより前に記述**する必要があります。Nginxは最初にマッチした`location`を使用するためです。

---

### オプション2: アプリケーション側でstatic_url_pathを通常に戻す

Flask側で`static_url_path`を通常の`/static`に戻し、Nginx側でリライトする方法。

#### ステップ1: `app.py`を修正

```python
# static_url_pathを通常の'/static'に戻す
app = Flask(__name__, static_url_path='/static')
```

#### ステップ2: Nginx側でリライト

```nginx
# /meetings/static へのアクセスを /static にリライト
location ~ ^/meetings/static/(.*)$ {
    rewrite ^/meetings/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:5002;
    # ... ヘッダー設定 ...
}
```

ただし、この場合、`url_for('static', ...)`が`/static/css/style.css`を生成するため、ブラウザは`/static/css/style.css`をリクエストします。この場合、Nginx側で`/static/css/style.css`を`/meetings/static/css/style.css`にリライトする必要があり、複雑です。

**推奨**: オプション1（Advancedタブでリライトルールを追加）

---

## 🧪 トラブルシューティング手順

### ステップ1: 現在の設定を確認

1. **Nginx Proxy ManagerのAdvancedタブを確認**
   - `http://192.168.68.110:8181` → Proxy Hosts → `yoshi-nas-sys.duckdns.org` → Advanced
   - Custom Nginx Configurationにリライトルールが追加されているか確認

2. **Custom Locationの設定を確認**
   - `/meetings`のCustom Locationが存在するか確認
   - Forward Hostname/IPが`192.168.68.110/`（末尾にスラッシュ）か確認

3. **アプリケーション側の設定を確認**

```bash
ssh -p 23456 AdminUser@192.168.68.110
cd /home/AdminUser/nas-project/meeting-minutes-byc
cat .env | grep SUBFOLDER_PATH
```

4. **Flask側のログを確認**

```bash
docker logs meeting-minutes-byc --tail 50
```

### ステップ2: リクエストの流れを確認

1. **ブラウザの開発者ツール → Networkタブ**
   - `style.css`のリクエストURLを確認: `https://yoshi-nas-sys.duckdns.org:8443/meetings/static/css/style.css`
   - ステータスコードを確認: 404かどうか
   - レスポンスヘッダーを確認: サーバー側の処理を確認

2. **Nginx Proxy Managerのログを確認**

```bash
ssh -p 23456 AdminUser@192.168.68.110
docker logs nginx-proxy-manager --tail 100 | grep meetings
```

### ステップ3: 設定の適用順序を確認

**重要**: Nginxの`location`ブロックは、最初にマッチしたものを使用します。そのため、リライトルールは**Custom Locationより前に記述**する必要があります。

現在の設定順序を確認：
1. AdvancedタブのCustom Nginx Configuration（最優先）
2. Custom Locationの設定（後）

---

## 📝 チェックリスト

- [ ] Nginx Proxy ManagerのAdvancedタブにリライトルールを追加したか
- [ ] リライトルールがCustom Locationより**前に**記述されているか
- [ ] Proxy Hostのステータスが「Online」のままか
- [ ] ブラウザのキャッシュをクリアしたか（`Cmd+Shift+R`または`Ctrl+Shift+R`）
- [ ] アプリケーション側の`.env`に`SUBFOLDER_PATH=/meetings`が設定されているか
- [ ] Dockerコンテナを再起動したか
- [ ] ブラウザの開発者ツールで404エラーの詳細を確認したか

---

## 🚨 緊急回避策

Advancedタブでの設定が難しい場合は、一時的にアプリケーション側の`static_url_path`を通常の`/static`に戻し、Nginx側で処理する方法を試してください。

```python
# app.py
app = Flask(__name__, static_url_path='/static')  # '/meetings/static'を'/static'に戻す
```

ただし、この場合、HTML内の`url_for('static', ...)`が`/static/css/style.css`を生成するため、別のリライトルールが必要になります。

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant



