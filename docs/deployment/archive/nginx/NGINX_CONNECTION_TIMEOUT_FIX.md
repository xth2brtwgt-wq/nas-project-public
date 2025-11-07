# 🔧 Nginx Proxy Manager 接続タイムアウト問題の解決

**作成日**: 2025-01-27  
**対象**: 「サーバとの接続が予期せず解除された」エラーの解決

---

## 📋 概要

「サーバとの接続が予期せず解除されたため、ページを開けません」というエラーが表示される問題の解決方法を説明します。

このエラーは、Nginx Proxy Managerとバックエンドサービス間の接続がタイムアウトしている、または接続が途中で切断されていることを示しています。

---

## 🔍 問題の原因

### 考えられる原因

1. **Nginx Proxy Managerのタイムアウト設定が短すぎる**
2. **バックエンドサービスの応答が遅い**
3. **Nginx Proxy Managerとバックエンドサービス間の接続が不安定**
4. **ファイアウォールが接続を途中で切断している**
5. **ネットワークの問題**

---

## ✅ 解決方法

### ステップ1: Nginx Proxy Managerのタイムアウト設定を確認・延長

**Custom Nginx Configurationに以下の設定を追加**:

```nginx
# ==========================================
# タイムアウト設定（接続タイムアウト対策）
# ==========================================

# 接続タイムアウト（デフォルト60秒 → 300秒に延長）
proxy_connect_timeout 300s;

# 送信タイムアウト（デフォルト60秒 → 300秒に延長）
proxy_send_timeout 300s;

# 受信タイムアウト（デフォルト60秒 → 300秒に延長）
proxy_read_timeout 300s;

# クライアント接続タイムアウト（デフォルト60秒 → 300秒に延長）
client_body_timeout 300s;
client_header_timeout 300s;

# キープアライブタイムアウト（接続を維持する時間を延長）
keepalive_timeout 300s;

# プロキシバッファリングを無効化（応答が遅い場合の対策）
proxy_buffering off;
proxy_request_buffering off;
```

**設定手順**:
1. **Nginx Proxy ManagerのWeb UIにアクセス**
   - `http://192.168.68.110:8181`

2. **Proxy Hosts → yoshi-nas-sys.duckdns.org → Advanced → Custom Nginx Configuration**

3. **既存のタイムアウト設定を確認**
   - 既存のタイムアウト設定がある場合は、上記の設定に置き換える

4. **上記の設定を追加または更新**

5. **「Save」をクリック**

---

### ステップ2: バックエンドサービスの応答時間を確認

**NAS環境で実行**:
```bash
# 各サービスの応答時間を測定
time curl -I http://192.168.68.110:9001
time curl -I http://192.168.68.110:8001
time curl -I http://192.168.68.110:3002
time curl -I http://192.168.68.110:5002
time curl -I http://192.168.68.110:8080
time curl -I http://192.168.68.110:8111
```

**確認項目**:
- 各サービスの応答時間が5秒以内か
- タイムアウトが発生していないか
- エラーが発生していないか

---

### ステップ3: Nginx Proxy Managerのログを確認

**NAS環境で実行**:
```bash
# Nginx Proxy Managerのエラーログを確認
docker logs nginx-proxy-manager --tail 200 | grep -i "timeout\|error\|connection"

# アクセスログを確認
docker exec nginx-proxy-manager tail -100 /data/logs/proxy-host-6_access.log

# エラーログを確認
docker exec nginx-proxy-manager tail -100 /data/logs/proxy-host-6_error.log
```

**確認項目**:
- タイムアウトエラーがないか
- 接続エラーがないか
- 502 Bad Gatewayエラーがないか

---

### ステップ4: バックエンドサービスのログを確認

**NAS環境で実行**:
```bash
# 各サービスのログを確認
docker logs nas-dashboard --tail 100 | grep -i "error\|timeout\|slow"
docker logs nas-dashboard-monitoring-backend --tail 100 | grep -i "error\|timeout\|slow"
docker logs amazon-analytics --tail 100 | grep -i "error\|timeout\|slow"
docker logs meeting-minutes-byc --tail 100 | grep -i "error\|timeout\|slow"
docker logs document-automation --tail 100 | grep -i "error\|timeout\|slow"
docker logs youtube-to-notion --tail 100 | grep -i "error\|timeout\|slow"
```

**確認項目**:
- エラーログがないか
- タイムアウトが発生していないか
- 処理が遅い箇所がないか

---

### ステップ5: ファイアウォールの設定を確認

**NAS管理画面で確認**:
1. **セキュリティ → ファイアウォール** を開く

2. **ファイアウォールの状態を確認**
   - ファイアウォールが有効化されているか確認
   - ルールの順序を確認

3. **ルール2（8443ポート）の設定を確認**
   - タイプが「ターゲットポート」になっているか確認
   - ポート番号が8443になっているか確認
   - ソースIPが「すべて」になっているか確認

---

### ステップ6: Nginx Proxy Managerを再起動

**NAS環境で実行**:
```bash
# Nginx Proxy Managerを再起動
docker restart nginx-proxy-manager

# 再起動後のログを確認
docker logs nginx-proxy-manager --tail 50
```

---

## 🔍 トラブルシューティング

### 問題1: タイムアウト設定を追加したが、まだタイムアウトが発生する

**確認項目**:
- タイムアウト設定が正しく追加されているか
- バックエンドサービスの応答時間がタイムアウト設定より長いか

**解決方法**:
- タイムアウト設定をさらに延長する（例: 300秒 → 600秒）
- バックエンドサービスの応答時間を改善する

---

### 問題2: バックエンドサービスの応答が遅い

**確認項目**:
- データベース接続が遅いか
- 外部APIの応答が遅いか
- 処理が重いか

**解決方法**:
- データベース接続の最適化
- 外部APIの応答時間を改善
- 処理の最適化

---

### 問題3: 接続が途中で切断される

**確認項目**:
- ファイアウォールが接続を切断していないか
- ネットワークが不安定でないか

**解決方法**:
- ファイアウォールの設定を確認
- ネットワークの安定性を確認
- キープアライブ設定を追加

---

## 📊 推奨されるタイムアウト設定

### 標準的な設定（推奨）

```nginx
# 接続タイムアウト
proxy_connect_timeout 300s;

# 送信タイムアウト
proxy_send_timeout 300s;

# 受信タイムアウト
proxy_read_timeout 300s;

# クライアント接続タイムアウト
client_body_timeout 300s;
client_header_timeout 300s;

# キープアライブタイムアウト
keepalive_timeout 300s;
```

### 長時間処理が必要な場合

```nginx
# 接続タイムアウト（10分）
proxy_connect_timeout 600s;

# 送信タイムアウト（10分）
proxy_send_timeout 600s;

# 受信タイムアウト（10分）
proxy_read_timeout 600s;

# クライアント接続タイムアウト（10分）
client_body_timeout 600s;
client_header_timeout 600s;

# キープアライブタイムアウト（10分）
keepalive_timeout 600s;
```

---

## ⚠️ 重要な注意事項

### タイムアウト設定を延長しすぎない

- ⚠️ **タイムアウト設定を延長しすぎると、リソースを消費し続ける可能性があります**
- ✅ **必要最小限のタイムアウト設定を推奨します**

### バックエンドサービスの応答時間を改善する

- ⚠️ **タイムアウト設定を延長するよりも、バックエンドサービスの応答時間を改善する方が効果的です**
- ✅ **バックエンドサービスの処理を最適化することを推奨します**

---

## 📚 参考資料

- **Nginx Proxy Manager最終設定**: `docs/deployment/NGINX_FINAL_CONFIG.md`
- **Nginx Proxy Manager画面が表示されない・読み込みが遅い問題の解決**: `docs/deployment/NGINX_SLOW_RESPONSE_TROUBLESHOOTING.md`
- **ファイアウォール設定ガイド**: `docs/deployment/NAS_BUILTIN_FIREWALL_SETUP.md`

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

