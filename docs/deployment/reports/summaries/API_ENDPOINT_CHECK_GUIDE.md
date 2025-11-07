# 🔍 APIエンドポイント設定確認ガイド

**作成日**: 2025-01-27  
**対象**: `/monitoring/api/v1/auth/check` エンドポイントの設定確認

---

## 📋 概要

アクセスログの分析結果から、`/monitoring/api/v1/auth/check` エンドポイントで404エラーが発生していることが確認されました。このエンドポイントの設定を確認し、必要に応じて修正します。

---

## 🔍 確認項目

### 1. バックエンドAPIエンドポイントの定義

**ファイル**: `nas-dashboard-monitoring/app/main.py`

```166:189:nas-dashboard-monitoring/app/main.py
@app.get("/api/v1/auth/check")
async def check_auth(request: Request):
    """認証状態を確認するエンドポイント（認証チェック専用）"""
    # 認証チェック専用なので、require_authを使わずに直接確認
    # リダイレクトは行わず、認証状態のみを返す
    if not AUTH_ENABLED:
        return {
            "authenticated": True,  # 認証が無効な場合は認証済みとして扱う
            "username": None
        }
    
    user = get_current_user_from_request(request)
    if user:
        logger.info(f"[AUTH] check_auth: 認証成功 - {user.get('username')}")
        return {
            "authenticated": True,
            "username": user.get("username")
        }
    # 認証されていない場合は200を返してauthenticated: falseを返す
    # リダイレクトはフロントエンドで処理
    logger.info(f"[AUTH] check_auth: 認証失敗")
    return {
        "authenticated": False
    }
```

**確認結果**: ✅ **エンドポイントは正しく定義されています**

---

### 2. Nginx Proxy Managerの設定

**設定ファイル**: Nginx Proxy ManagerのWeb UI → Proxy Hosts → yoshi-nas-sys.duckdns.org → Advanced → Custom Nginx Configuration

**推奨設定**:
```nginx
# /monitoring のAPI修正（nas-dashboard-monitoring - バックエンドに直接転送）
location ~ ^/monitoring/api/(.*)$ {
    rewrite ^/monitoring/api/(.*)$ /api/$1 break;
    proxy_pass http://192.168.68.110:8002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    auth_basic off;
}
```

**確認方法**:
1. Nginx Proxy ManagerのWeb UIにアクセス
2. Proxy Hosts → yoshi-nas-sys.duckdns.org を選択
3. Advanced タブを開く
4. Custom Nginx Configuration を確認

**期待される動作**:
- `/monitoring/api/v1/auth/check` → `/api/v1/auth/check` にリライト
- `http://192.168.68.110:8002/api/v1/auth/check` にプロキシ

---

### 3. バックエンドサービスの状態確認

**確認コマンド**:
```bash
# バックエンドサービスの状態を確認
docker ps | grep nas-dashboard-monitoring

# バックエンドサービスのログを確認
docker logs nas-dashboard-monitoring-backend-1 --tail 50

# バックエンドサービスに直接アクセスして確認
curl http://192.168.68.110:8002/api/v1/auth/check
```

**期待される結果**:
- コンテナが稼働中であること
- `/api/v1/auth/check` エンドポイントが正常に応答すること

---

## 🔧 トラブルシューティング

### 404エラーが発生する場合

1. **Nginx Proxy Managerの設定を確認**
   - Custom Nginx Configuration に `/monitoring/api/(.*)` の設定が存在するか確認
   - 設定が存在しない場合は追加

2. **バックエンドサービスの状態を確認**
   - コンテナが稼働中であること
   - ポート8002が正しく公開されていること

3. **リライトルールを確認**
   - `/monitoring/api/v1/auth/check` が `/api/v1/auth/check` に正しくリライトされているか確認

---

## 📊 確認手順

### ステップ1: Nginx Proxy Managerの設定を確認

1. Nginx Proxy ManagerのWeb UIにアクセス
2. Proxy Hosts → yoshi-nas-sys.duckdns.org を選択
3. Advanced タブを開く
4. Custom Nginx Configuration を確認

### ステップ2: バックエンドサービスの状態を確認

```bash
# NAS環境で実行
ssh -p 23456 AdminUser@192.168.68.110

# バックエンドサービスの状態を確認
docker ps | grep nas-dashboard-monitoring

# バックエンドサービスに直接アクセス
curl http://192.168.68.110:8002/api/v1/auth/check
```

### ステップ3: エンドポイントの動作確認

```bash
# 外部からアクセスして確認
curl https://yoshi-nas-sys.duckdns.org:8443/monitoring/api/v1/auth/check
```

---

## 📚 参考資料

- **セキュリティ対策設定状況の確認結果**: `docs/deployment/SECURITY_STATUS_VERIFICATION.md`
- **Nginx Proxy Managerアクセスログ分析ガイド**: `docs/deployment/NGINX_ACCESS_LOG_ANALYSIS.md`
- **Nginx Proxy Manager設定ガイド**: `docs/deployment/NGINX_PROXY_MANAGER_SETUP_COMPLETE.md`

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

