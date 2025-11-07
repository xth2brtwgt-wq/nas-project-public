# 📍 meeting-minutes-byc - ローカルアクセスと外部アクセスの違い

**作成日**: 2025-11-02  
**目的**: ローカルアクセスと外部アクセスの設定方法を説明

---

## 🔍 アクセス方法の違い

### 方法1: 直接アプリケーションにアクセス（ローカル推奨）

#### 設定
`.env`ファイルで`SUBFOLDER_PATH`を空にする（またはコメントアウト）：

```bash
# 内部ネットワークからの直接アクセスの場合
SUBFOLDER_PATH=

# または、コメントアウト
# SUBFOLDER_PATH=/meetings
```

#### アクセスURL
```
http://192.168.68.110:5002
```

#### メリット
- シンプルで直接アクセスできる
- Nginx Proxy Managerを経由しない
- Basic認証が不要（開発時に便利）

#### デメリット
- HTTPSではない
- 外部からアクセスできない

---

### 方法2: Nginx Proxy Manager経由でアクセス（外部・統一アクセス）

#### 設定
`.env`ファイルで`SUBFOLDER_PATH`を設定：

```bash
# 外部ネットワークからのアクセスの場合
SUBFOLDER_PATH=/meetings
```

#### アクセスURL
```
https://yoshi-nas-sys.duckdns.org:8443/meetings
```

#### メリット
- HTTPSで安全
- 外部からアクセスできる
- ローカルからも外部と同じURLでアクセスできる（統一性）
- Basic認証で保護されている

#### デメリット
- Nginx Proxy Manager経由のため、少し遅い可能性がある

---

## 📝 現在の設定

現在の設定（`SUBFOLDER_PATH=/meetings`）では、外部からのアクセスと同じURLでアクセスする必要があります。

### ローカルから直接アクセスしたい場合

1. **`.env`ファイルを編集**:

```bash
# 内部ネットワークからの直接アクセスの場合
SUBFOLDER_PATH=
```

2. **Dockerコンテナを再起動**:

```bash
docker compose restart meeting-minutes-byc
```

3. **直接アクセス**:

```
http://192.168.68.110:5002
```

### ローカルからも外部と同じURLでアクセスしたい場合

現在の設定（`SUBFOLDER_PATH=/meetings`）のまま、以下のURLでアクセス：

```
https://yoshi-nas-sys.duckdns.org:8443/meetings
```

**注意**: Basic認証が必要です。

---

## 🔄 設定の切り替え

### 開発時（ローカル直接アクセス）

```bash
# .envファイルを編集
SUBFOLDER_PATH=

# コンテナを再起動
docker compose restart meeting-minutes-byc

# アクセス
http://192.168.68.110:5002
```

### 本番環境（外部アクセス）

```bash
# .envファイルを編集
SUBFOLDER_PATH=/meetings

# コンテナを再起動
docker compose restart meeting-minutes-byc

# アクセス
https://yoshi-nas-sys.duckdns.org:8443/meetings
```

---

## 💡 推奨事項

### 開発時
- `SUBFOLDER_PATH`を空にして、直接`http://192.168.68.110:5002`でアクセス
- Basic認証が不要で、開発がしやすい

### 本番環境
- `SUBFOLDER_PATH=/meetings`を設定して、Nginx Proxy Manager経由でアクセス
- HTTPSで安全、外部からアクセス可能

### 両方をサポートしたい場合
環境変数で切り替え可能にしておく（現在の実装で可能）：

```bash
# 内部ネットワークからの直接アクセス
SUBFOLDER_PATH=

# 外部ネットワークからのアクセス
SUBFOLDER_PATH=/meetings
```

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant


