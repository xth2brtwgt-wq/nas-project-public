# 📊 Nginx Proxy Manager アクセスログ分析ガイド

**作成日**: 2025-01-27  
**対象**: Nginx Proxy Managerのアクセスログを分析する方法

---

## 📋 概要

Nginx Proxy Managerのアクセスログを分析し、異常なアクセスパターンやセキュリティ上の問題を特定する方法を説明します。

---

## 🔍 アクセスログの分析結果（2025-11-07時点）

### 基本情報

- **ログファイル**: `/data/logs/proxy-host-6_access.log` (約5MB)
- **エラーログ**: `/data/logs/proxy-host-6_error.log` (約291KB)
- **主なアクセス元**: `58.183.58.145` (ユーザー自身のIPアドレス)

---

## 📊 アクセスログの分析

### 1. アクセス数の多いIPアドレス

```bash
# アクセス数の多いIPアドレスを確認
docker exec nginx-proxy-manager awk '{print $1}' /data/logs/proxy-host-6_access.log | sort | uniq -c | sort -rn | head -10
```

**結果の解釈**:
- 主なアクセス元はユーザー自身のIPアドレス（正常）
- 異常に多いアクセス数のIPアドレスがないか確認

---

### 2. ステータスコード別のアクセス数

```bash
# ステータスコード別のアクセス数を確認
docker exec nginx-proxy-manager awk '{print $9}' /data/logs/proxy-host-6_access.log | sort | uniq -c | sort -rn
```

**確認結果**:
- **200**: 正常なアクセス（大部分）
- **404**: 存在しないリソースへのアクセス
- **401**: Basic認証による正常な認証要求
- **302**: リダイレクト（正常）

---

### 3. 404エラーの詳細

```bash
# 404エラーの詳細を確認
docker exec nginx-proxy-manager grep " 404 " /data/logs/proxy-host-6_access.log | tail -20
```

**確認結果**:
- `/monitoring/api/v1/auth/check`: APIエンドポイントが存在しない（設定の問題の可能性）
- `/upload`: アップロードエンドポイントが存在しない（設定の問題の可能性）
- `/https://yoshi-nas-sys.duckdns.org:8443/login?next=%2Fdocuments`: 不正なURL（設定の問題の可能性）

**推奨される対応**:
1. APIエンドポイントの設定を確認
2. アップロードエンドポイントの設定を確認
3. リダイレクト設定を確認

---

### 4. 401/403エラーの詳細

```bash
# 401/403エラーの詳細を確認
docker exec nginx-proxy-manager grep -E " 401 | 403 " /data/logs/proxy-host-6_access.log | tail -20
```

**確認結果**:
- **401エラー**: Basic認証による正常な認証要求
  - ユーザー自身のアクセス（正常）
  - ソーシャルメディアのクローラー（facebookexternalhit、Twitterbot）によるアクセス（正常）
  - 外部からのアクセス試行（セキュリティ対策として正常）

**評価**:
- ✅ **Basic認証が正常に機能している**
- ✅ **未認証のアクセスが適切にブロックされている**

---

### 5. エラーログの分析

```bash
# エラーログを確認
docker exec nginx-proxy-manager tail -100 /data/logs/proxy-host-6_error.log
```

**確認結果**:
- **接続拒否エラー（Connection refused）**: 一部のサービスが停止していた可能性
  - `nas-dashboard` (ポート9001)
  - `nas-dashboard-monitoring` (ポート8002)
- **重複ヘッダー警告（duplicate header line）**: バックエンドアプリケーションが重複したDateヘッダーを送信している
  - `meeting-minutes-byc` (ポート5002)
  - `youtube-to-notion` (ポート8111)

**推奨される対応**:
1. サービスが停止していた原因を確認
2. バックエンドアプリケーションのヘッダー送信処理を修正

---

## 🔍 異常なアクセスパターンの検出

### 1. 不正なアクセス試行の検出

```bash
# 不正なアクセスパターンを確認
docker exec nginx-proxy-manager grep -i "401\|403\|404" /data/logs/proxy-host-6_access.log | tail -50

# 特定のIPアドレスからの異常なアクセスを確認
docker exec nginx-proxy-manager grep "192.168.68.110" /data/logs/proxy-host-6_access.log | tail -20
```

---

### 2. 異常なリクエストパスの検出

```bash
# 異常なリクエストパスを確認
docker exec nginx-proxy-manager awk '{print $7}' /data/logs/proxy-host-6_access.log | sort | uniq -c | sort -rn | head -20
```

---

### 3. 異常なUser-Agentの検出

```bash
# 異常なUser-Agentを確認
docker exec nginx-proxy-manager awk -F'"' '{print $6}' /data/logs/proxy-host-6_access.log | sort | uniq -c | sort -rn | head -20
```

---

## 📊 ログ分析の自動化

### 推奨される監視項目

1. **異常なアクセスパターンの検出**
   - 短時間に大量のアクセス
   - 404エラーの急増
   - 401/403エラーの急増

2. **異常なIPアドレスの検出**
   - 未知のIPアドレスからのアクセス
   - 特定のIPアドレスからの異常なアクセス

3. **エラーログの監視**
   - 接続拒否エラーの増加
   - タイムアウトエラーの増加

---

## 🔧 トラブルシューティング

### 404エラーが多発している場合

1. **APIエンドポイントの設定を確認**
   - Nginx Proxy Managerの設定を確認
   - バックエンドアプリケーションの設定を確認

2. **リダイレクト設定を確認**
   - リダイレクトルールが正しく設定されているか確認

---

### 接続拒否エラーが多発している場合

1. **サービスの状態を確認**
   ```bash
   docker ps | grep nas-dashboard
   docker ps | grep nas-dashboard-monitoring
   ```

2. **サービスのログを確認**
   ```bash
   docker logs nas-dashboard --tail 100
   docker logs nas-dashboard-monitoring-backend-1 --tail 100
   ```

---

### 重複ヘッダー警告が多発している場合

1. **バックエンドアプリケーションのヘッダー送信処理を確認**
   - Dateヘッダーが重複して送信されていないか確認
   - フレームワークの設定を確認

---

## 📚 参考資料

- **セキュリティ対策設定状況の確認結果**: `docs/deployment/SECURITY_STATUS_VERIFICATION.md`
- **Nginx Proxy Managerアクセスログ確認ガイド**: `docs/deployment/NGINX_ACCESS_LOG_CHECK.md`
- **Nginx Proxy Managerログファイルの場所確認ガイド**: `docs/deployment/NGINX_LOG_LOCATION_CHECK.md`

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

