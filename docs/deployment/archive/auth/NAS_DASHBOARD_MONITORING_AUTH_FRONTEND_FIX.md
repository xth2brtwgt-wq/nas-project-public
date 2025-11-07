# 🔧 NAS Dashboard Monitoring フロントエンド認証修正

**作成日**: 2025-11-04  
**目的**: `nas-dashboard-monitoring`のフロントエンド静的ファイルへの認証を追加

---

## ❌ 問題

`nas-dashboard-monitoring`のフロントエンド（React）の静的ファイルが認証なしでアクセス可能になっています。

```bash
curl -v https://yoshi-nas-sys.duckdns.org:8443/monitoring
```

**結果**:
- HTTP 200（リダイレクトされていない）
- HTMLコンテンツが返されている

---

## 🔍 原因

`nas-dashboard-monitoring`はフロントエンド（React）とバックエンド（FastAPI）が分離されています：

1. **フロントエンド**: Reactアプリ（静的ファイル）
   - `/monitoring` → Nginx Proxy Managerから直接配信
   - `/monitoring/static/...` → Nginx Proxy Managerから直接配信

2. **バックエンド**: FastAPI（API）
   - `/monitoring/api/...` → バックエンドにプロキシ
   - 認証チェックが実装されている

フロントエンドの静的ファイルは認証チェックの対象外になっているため、直接アクセス可能になっています。

---

## ✅ 解決策

### オプション1: フロントエンド側で認証チェック（推奨）

フロントエンドのReactアプリ側で認証チェックを行い、未認証の場合はログインページにリダイレクトします。

#### メリット
- ユーザー体験が良い（フロントエンド側で即座にリダイレクト）
- バックエンドAPIへの不要なリクエストを減らせる

#### デメリット
- フロントエンドコードの修正が必要
- 静的ファイル自体は認証なしでダウンロード可能（ただし、JavaScriptコードは難読化されている）

### オプション2: Nginx Proxy ManagerでBasic認証を有効化

フロントエンドの静的ファイルにもBasic認証を適用します。

#### メリット
- 実装が簡単（Nginx Proxy Managerの設定のみ）
- 静的ファイル自体も保護される

#### デメリット
- ダッシュボード認証とBasic認証の二重認証になる
- ユーザー体験が悪い

### オプション3: フロントエンドをバックエンド経由で配信

フロントエンドの静的ファイルをバックエンド経由で配信し、バックエンドで認証チェックを行います。

#### メリット
- 認証チェックを一箇所で管理できる
- 静的ファイルも保護される

#### デメリット
- バックエンドの負荷が増える
- 実装が複雑

---

## 🚀 推奨実装（オプション1）

フロントエンド側で認証チェックを実装します。

### ステップ1: 認証チェック用のAPIエンドポイントを追加

バックエンドに認証状態を確認するエンドポイントを追加します：

```python
@app.get("/api/v1/auth/check")
async def check_auth(user: Optional[Dict] = Depends(require_auth)):
    """認証状態を確認"""
    if user:
        return {"authenticated": True, "username": user.get("username")}
    return {"authenticated": False}
```

### ステップ2: フロントエンドで認証チェック

Reactアプリの起動時に認証チェックを行い、未認証の場合はログインページにリダイレクトします。

```typescript
// App.tsx
useEffect(() => {
  const checkAuth = async () => {
    try {
      const response = await fetch(apiPath('/api/v1/auth/check'));
      const data = await response.json();
      if (!data.authenticated) {
        window.location.href = 'https://yoshi-nas-sys.duckdns.org:8443/login';
      }
    } catch (error) {
      console.error('認証チェックエラー:', error);
      window.location.href = 'https://yoshi-nas-sys.duckdns.org:8443/login';
    }
  };
  
  checkAuth();
}, []);
```

---

## 📝 現在の状態

### バックエンドAPI

バックエンドAPIは認証が正常に機能しています：

```bash
curl -v https://yoshi-nas-sys.duckdns.org:8443/monitoring/api/v1/metrics
```

**期待される結果**:
- HTTP 307（リダイレクト）
- `location: https://yoshi-nas-sys.duckdns.org:8443/login`

### フロントエンド静的ファイル

フロントエンドの静的ファイルは認証なしでアクセス可能です：

```bash
curl -v https://yoshi-nas-sys.duckdns.org:8443/monitoring
```

**結果**:
- HTTP 200
- HTMLコンテンツが返される

ただし、フロントエンドがAPIを呼び出す際に認証チェックが行われるため、実際の機能は使用できません。

---

## 🔧 一時的な対応

現時点では、フロントエンドの静的ファイルは認証なしでアクセス可能ですが、APIアクセス時に認証チェックが行われるため、実際の機能は使用できません。

より厳密な認証が必要な場合は、上記のオプション1を実装することを推奨します。

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

