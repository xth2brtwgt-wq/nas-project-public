# 🔧 アプリケーション側でサブフォルダ対応設定

**作成日**: 2025-11-02  
**目的**: 各アプリケーションをサブフォルダ配信に対応させる

---

## 📋 対象アプリケーション

Nginx Proxy ManagerでCustom Locationを使用している以下のアプリケーション：

- **meeting-minutes-byc**: `/meetings`
- **amazon-analytics**: `/analytics`（今後対応）
- **document-automation**: `/documents`（今後対応）
- **nas-dashboard-monitoring**: `/monitoring`（今後対応）
- **youtube-to-notion**: `/youtube`（今後対応）

---

## ✅ meeting-minutes-byc の設定

### ステップ1: app.pyの編集

`meeting-minutes-byc/app.py`でFlask初期化部分を修正しました。

**変更内容**:
- `APPLICATION_ROOT`を設定（`/meetings`）
- `SESSION_COOKIE_PATH`を設定（`/meetings`）
- 環境変数`SUBFOLDER_PATH`で制御可能

### ステップ2: 環境変数の設定（オプション）

`.env`ファイルに以下を追加できます（外部アクセス時のみ）：

```bash
# サブフォルダ対応（Nginx Proxy Manager経由でアクセスする場合）
SUBFOLDER_PATH=/meetings
```

**注意**: 
- 内部ネットワークから直接アクセスする場合（`http://192.168.68.110:5002`）は、環境変数を設定しないか、`SUBFOLDER_PATH=/`に設定
- 外部からNginx Proxy Manager経由でアクセスする場合のみ、`SUBFOLDER_PATH=/meetings`を設定

### ステップ3: デプロイ

```bash
cd /home/AdminUser/nas-project/meeting-minutes-byc
docker compose down
docker compose build
docker compose up -d
```

---

## 🔍 動作確認

### 外部からのアクセス

1. **`https://yoshi-nas-sys.duckdns.org:8443/meetings`にアクセス**

2. **ブラウザの開発者ツールで確認**:
   - CSSファイル: `https://yoshi-nas-sys.duckdns.org:8443/meetings/static/css/style.css`
   - JavaScriptファイル: `https://yoshi-nas-sys.duckdns.org:8443/meetings/static/js/app.js`
   - これらのパスで正しく読み込まれることを確認

3. **CSSが正しく適用されているか確認**

---

## 📝 他のアプリケーションへの対応

### amazon-analytics

今後、同様の対応が必要な場合：

```python
# app/api/main.py など
app.config['APPLICATION_ROOT'] = '/analytics'
```

### document-automation

```python
app.config['APPLICATION_ROOT'] = '/documents'
```

### nas-dashboard-monitoring

Reactアプリケーションの場合は、ビルド時のベースパス設定が必要。

### youtube-to-notion

Flaskアプリケーションの場合は、同様の設定が必要。

---

## ✅ チェックリスト

- [ ] `meeting-minutes-byc/app.py`を編集
- [ ] 必要に応じて`.env`ファイルに`SUBFOLDER_PATH=/meetings`を追加
- [ ] デプロイ（docker compose down → build → up）
- [ ] 外部からアクセスしてCSSが適用されることを確認
- [ ] 内部ネットワークから直接アクセスしても動作することを確認

---

## 📚 参考資料

- [Flask APPLICATION_ROOT](https://flask.palletsprojects.com/en/latest/config/#APPLICATION_ROOT)
- [Flask SESSION_COOKIE_PATH](https://flask.palletsprojects.com/en/latest/config/#SESSION_COOKIE_PATH)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant



