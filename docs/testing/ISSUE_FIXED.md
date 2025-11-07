# 解決した問題 - amazon-analytics

**日時**: 2025-10-21

---

## 🐛 問題

amazon-analytics の起動時に以下のエラーが発生：

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
POSTGRES_PASSWORD
  Extra inputs are not permitted [type=extra_forbidden, input_value='your_secure_password_here', input_type=str]
```

### 原因

1. **Settings クラスに `POSTGRES_PASSWORD` フィールドが未定義**
   - `.env` に `POSTGRES_PASSWORD` が設定されている
   - しかし、`Settings` クラスには定義されていない
   - Pydantic v2 ではデフォルトで extra inputs が禁止されている

2. **データベースパスワード不一致**
   - 既存のデータベースボリュームに古いパスワードが残っていた
   - 新しいパスワードで接続しようとして認証エラー

---

## ✅ 解決策

### 1. Settings クラスの修正

**ファイル**: `amazon-analytics/config/settings.py`

#### 追加したフィールド:
```python
# Database
POSTGRES_PASSWORD: Optional[str] = "postgres"
DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/amazon_analytics"
```

#### Config クラスの修正:
```python
class Config:
    env_file = ".env"
    case_sensitive = False  # 変更: True → False
    extra = "allow"  # 追加: 追加の環境変数を許可
```

### 2. データベースボリュームのリセット

```bash
cd amazon-analytics
docker-compose down -v  # ボリュームを削除
docker-compose up -d     # 再起動
```

---

## 🎯 結果

```
✅ Database initialized
✅ Application startup complete
✅ Uvicorn running on http://0.0.0.0:8000
```

amazon-analytics が正常に起動！

---

## 📝 今後の注意点

### 1. **Pydantic Settings の使用**

Pydantic v2 では、デフォルトで extra inputs が禁止されています。

**対策**:
- 環境変数として使用するフィールドはすべて Settings クラスに定義
- または `extra = "allow"` を設定

### 2. **データベースパスワードの変更**

パスワードを変更する場合：
```bash
docker-compose down -v  # 既存のボリュームを削除
# .env を編集
docker-compose up -d     # 新しいパスワードで起動
```

### 3. **docker-compose.yml の警告**

以下の警告が出ています：
```
WARN: the attribute `version` is obsolete
WARN: The "GEMINI_API_KEY" variable is not set
```

**修正方法**:
1. `version: '3.8'` の行を削除（obsolete）
2. `.env` に `GEMINI_API_KEY` を設定

---

## 🔄 適用すべき修正

他のプロジェクトでも同様の問題が発生する可能性があります。

### チェックリスト:
- [ ] document-automation
- [ ] insta360-auto-sync
- [ ] meeting-minutes-byc

---

**修正完了**: 2025-10-21  
**テスト**: ✅ 成功

