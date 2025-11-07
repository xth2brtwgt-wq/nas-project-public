# 🚀 Meeting Minutes BYC - サブフォルダ対応デプロイ手順

**作成日**: 2025-11-02  
**目的**: meeting-minutes-bycをサブフォルダ（/meetings）対応にする

---

## 📋 変更内容

### app.pyの変更

Flaskアプリケーションに`APPLICATION_ROOT`を設定して、サブフォルダ対応にしました。

**変更点**:
- `APPLICATION_ROOT = '/meetings'`を設定（環境変数で制御）
- `SESSION_COOKIE_PATH = '/meetings'`を設定
- 環境変数`SUBFOLDER_PATH`で制御可能

---

## 🚀 デプロイ手順

### ステップ1: NASにSSH接続

```bash
ssh -p 23456 AdminUser@192.168.68.110
```

### ステップ2: プロジェクトディレクトリに移動

```bash
cd /home/AdminUser/nas-project/meeting-minutes-byc
```

### ステップ3: 最新コードを取得

```bash
git pull origin main
```

### ステップ4: 環境変数の設定

`.env`ファイルを編集：

```bash
nano .env
```

**以下の行を追加**（外部アクセス時のみ）:

```bash
# Subfolder Support (Nginx Proxy Manager経由でアクセスする場合)
SUBFOLDER_PATH=/meetings
```

**注意**: 
- **内部ネットワークから直接アクセスする場合**（`http://192.168.68.110:5002`）は、この環境変数を**設定しない**か、**コメントアウト**してください
- **外部からNginx Proxy Manager経由でアクセスする場合のみ**、`SUBFOLDER_PATH=/meetings`を設定してください

### ステップ5: Dockerコンテナを再ビルド・再起動

```bash
# コンテナを停止
docker compose down

# イメージを再ビルド
docker compose build

# コンテナを起動
docker compose up -d

# ログを確認
docker compose logs -f
```

---

## ✅ 動作確認

### 外部からのアクセス

1. **`https://yoshi-nas-sys.duckdns.org:8443/meetings`にアクセス**

2. **ブラウザの開発者ツールで確認**:
   - CSSファイル: `https://yoshi-nas-sys.duckdns.org:8443/meetings/static/css/style.css`
   - JavaScriptファイル: `https://yoshi-nas-sys.duckdns.org:8443/meetings/static/js/app.js`
   - これらのパスで正しく読み込まれることを確認（200 OK）

3. **CSSが正しく適用されているか確認**

### 内部ネットワークからのアクセス

1. **`http://192.168.68.110:5002`にアクセス**

2. **正常に動作することを確認**（環境変数を設定していない場合）

---

## 🔍 トラブルシューティング

### CSSが適用されない場合

1. **ブラウザの開発者ツールで静的ファイルのURLを確認**
   - `/meetings/static/css/style.css`になっているか確認

2. **環境変数が正しく設定されているか確認**:
   ```bash
   docker compose exec meeting-minutes-byc env | grep SUBFOLDER_PATH
   ```

3. **アプリケーションログを確認**:
   ```bash
   docker compose logs meeting-minutes-byc | grep "サブフォルダ対応"
   ```

### 内部ネットワークからアクセスできない場合

`.env`ファイルから`SUBFOLDER_PATH`を削除またはコメントアウト：

```bash
# SUBFOLDER_PATH=/meetings
```

コンテナを再起動：

```bash
docker compose restart
```

---

## 📝 チェックリスト

- [ ] `meeting-minutes-byc/app.py`が最新版に更新されている（git pull）
- [ ] `.env`ファイルに`SUBFOLDER_PATH=/meetings`を追加（外部アクセス時のみ）
- [ ] Dockerコンテナを再ビルド・再起動
- [ ] 外部からアクセスしてCSSが適用されることを確認
- [ ] 内部ネットワークから直接アクセスしても動作することを確認

---

## 📚 参考資料

- [アプリケーション側でサブフォルダ対応設定](APPLICATION_SUBFOLDER_SUPPORT_SETUP.md)
- [Flask APPLICATION_ROOT](https://flask.palletsprojects.com/en/latest/config/#APPLICATION_ROOT)

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant



