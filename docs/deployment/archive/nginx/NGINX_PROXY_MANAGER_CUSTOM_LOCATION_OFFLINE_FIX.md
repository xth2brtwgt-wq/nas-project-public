# 🔧 Nginx Proxy Manager - Custom Location追加でOfflineになる問題の解決

**作成日**: 2025-11-02  
**目的**: Custom Locationに設定を追加するとProxy HostがOfflineになる問題を解決

---

## ⚠️ 問題

Custom Locationの「Custom Nginx configuration」に設定を追加すると、Proxy Hostのステータスが「Offline」になる。

---

## 🔍 原因の確認

### 考えられる原因

1. **Custom Location内での設定構文エラー**
2. **Nginx設定ファイルの生成失敗**
3. **Custom Locationの設定方法の問題**

---

## ✅ 段階的な解決手順

### ステップ1: Custom Locationの設定をクリア

まず、Custom Locationの「Custom Nginx configuration」を完全に空にして、Proxy Hostがオンラインに戻るか確認します。

1. **Custom Locationの`/meetings`を編集**

2. **「Custom Nginx configuration」を完全に空にする**（すべて削除）

3. **「Save」をクリック**

4. **Proxy Host全体を保存**

5. **Proxy Hostのステータスを確認**
   - 「Online」に戻ったか確認

---

### ステップ2: Forward Hostname/IPの設定を確認

Custom Locationの基本設定を確認します。

1. **「Define location」**: `/meetings` ✅

2. **「Forward Hostname/IP」**: `192.168.68.110/`（末尾にスラッシュ） ✅

3. **「Forward Port」**: `5002` ✅

4. **「Custom Nginx configuration」**: **空欄のまま**（何も追加しない）

5. **「Save」をクリック**

---

### ステップ3: 基本的な設定のみで動作確認

まずは、Custom Nginx configurationを空欄のまま、基本的な設定のみでアクセスできるか確認します。

1. **`https://yoshi-nas-sys.duckdns.org:8443/meetings`にアクセス**

2. **ページが表示されるか確認**（レイアウトが崩れていてもOK）

3. **ページが表示されれば、基本設定は正常に動作している**

---

## 🔧 静的ファイル問題の別の解決方法

Custom Location内で設定を追加できない場合、以下の方法を試します。

### 方法1: Proxy Host全体のAdvancedタブで設定

1. **Proxy Hostの「Advanced」タブを開く**

2. **「Custom Nginx Configuration」に以下を追加**:

```nginx
# 各Custom Locationより前に記述
location ~ ^/(analytics|documents|monitoring|meetings|youtube)/static/ {
    # 静的ファイルのリライト
    rewrite ^/(analytics|documents|monitoring|meetings|youtube)/static/(.*)$ /static/$1 break;
    
    # 各サービスのポート番号に応じて転送
    proxy_pass http://192.168.68.110:5002;
    
    # デフォルトのプロキシヘッダー
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**注意**: この方法も複雑で、各サービスに応じた条件分岐が必要になります。

---

### 方法2: アプリケーション側で対応（推奨・最確実）

各アプリケーション側でサブフォルダ対応にします。

#### meeting-minutes-bycの設定例

`meeting-minutes-byc/app.py`を編集：

```python
from flask import Flask, request

# ベースパスを設定
BASE_PATH = '/meetings'

app = Flask(__name__)

@app.before_request
def before_request():
    """リクエスト前にベースパスを設定"""
    if request.path.startswith(BASE_PATH):
        request.path = request.path[len(BASE_PATH):]
        request.script_root = BASE_PATH
```

---

### 方法3: 一時的な回避策

レイアウトが崩れても機能は動作する場合、一時的にこの状態で使用し、後でアプリケーション側で対応する。

---

## 📋 チェックリスト

### まず試すこと

- [ ] Custom Locationの「Custom Nginx configuration」を完全に空にする
- [ ] Proxy Hostを保存
- [ ] Proxy Hostのステータスが「Online」になることを確認
- [ ] `/meetings`にアクセスしてページが表示されることを確認

### 次に試すこと

- [ ] Proxy Host全体のAdvancedタブでリライトルールを追加（方法1）
- [ ] または、アプリケーション側でサブフォルダ対応にする（方法2）

---

## 🔍 トラブルシューティング

### Nginx Proxy Managerのログを確認

```bash
# NASにSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# Nginx Proxy Managerのログを確認
docker logs nginx-proxy-manager --tail 100 | grep -i error
```

### 設定ファイルの確認

```bash
# Nginx設定ファイルを確認
docker exec nginx-proxy-manager nginx -t

# エラーがあれば表示される
```

---

## 📚 参考資料

- [Nginx Proxy Manager公式ドキュメント](https://nginxproxymanager.com/)
- [Flask APPLICATION_ROOT](https://flask.palletsprojects.com/en/latest/config/#APPLICATION_ROOT)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant



