# ✅ ダッシュボードCookieパス修正

**作成日**: 2025-11-04  
**目的**: Cookieの`path`設定を追加してサブパスでもCookieを共有できるようにする

---

## ❌ 問題

ダッシュボードでログイン後、議事録システム（`/meetings`）に遷移してもログイン画面が表示されてしまいます。

ログには以下のように表示されていました：

```
meeting-minutes-byc  | 2025-11-04 16:21:53,383 - __main__ - INFO - [AUTH] 認証が必要です: / -> http://192.168.68.110:9001/login
meeting-minutes-byc  | 2025-11-04 16:21:53,384 - werkzeug - INFO - 192.168.208.1 - - [04/Nov/2025 16:21:53] "GET / HTTP/1.1" 302 -
```

---

## 🔍 原因

Cookieに`path`が設定されていなかったため、Cookieが現在のパス（`/login`）にのみ適用され、サブパス（`/meetings`など）ではCookieが共有されていませんでした。

デフォルトでは、Cookieは現在のパスにのみ適用されます。つまり、`/login`で設定されたCookieは`/`と`/login`にのみ適用され、`/meetings`には適用されません。

---

## ✅ 修正内容

`nas-dashboard/app.py`のCookie設定に`path='/'`を追加：

```python
response.set_cookie(
    'session_id',
    session_id,
    secure=True,
    samesite='None',
    httponly=True,
    max_age=1800,  # 30分
    path='/'  # すべてのパスでCookieを利用可能にする
)
```

これにより、Cookieがすべてのパス（`/`, `/login`, `/meetings`, `/analytics`など）で利用可能になります。

---

## 🚀 デプロイ手順

### ステップ1: コードをプル

```bash
cd ~/nas-project/nas-dashboard
git pull origin feature/monitoring-fail2ban-integration
```

### ステップ2: コンテナを再起動

```bash
sudo docker compose down
sudo docker compose up -d
```

### ステップ3: ログを確認

```bash
sudo docker compose logs -f nas-dashboard
```

### ステップ4: 動作確認

1. **ダッシュボードでログイン**
   - `https://yoshi-nas-sys.duckdns.org:8443` にアクセス
   - ユーザー名とパスワードでログイン

2. **ログイン後に議事録システムにアクセス**
   - ダッシュボードから「議事録作成システム」をクリック
   - または直接 `https://yoshi-nas-sys.duckdns.org:8443/meetings` にアクセス

**期待される動作**:
- ✅ 議事録システムの画面が表示される
- ✅ ログに `GET / HTTP/1.1" 200` が記録される
- ✅ 認証エラーが発生しない

---

## 🔍 Cookieの確認方法

ブラウザの開発者ツール（F12）でCookieを確認：

1. **Application**タブを開く
2. **Cookies**を選択
3. **`yoshi-nas-sys.duckdns.org`**を選択
4. **`session_id`**Cookieを確認

**期待される設定**:
- **Name**: `session_id`
- **Value**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`（UUID形式）
- **Domain**: `.yoshi-nas-sys.duckdns.org` または `yoshi-nas-sys.duckdns.org`
- **Path**: `/`
- **Expires**: ログインから30分後
- **HttpOnly**: ✅
- **Secure**: ✅
- **SameSite**: `None`

---

## 📝 注意事項

### SameSite=Noneの場合

`SameSite=None`を使用する場合、`secure=True`が必須です。これはHTTPSでのみ機能します。

### パスの設定

`path='/'`を設定することで、すべてのパスでCookieが利用可能になります。これにより、ダッシュボード（`/`）と各サービス（`/meetings`, `/analytics`など）でCookieが共有されます。

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

