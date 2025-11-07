# 🔍 サービス状態確認ガイド

**作成日**: 2025-01-27  
**対象**: 接続拒否エラーの原因調査とサービスの状態確認

---

## 📋 概要

アクセスログの分析結果から、接続拒否エラー（Connection refused）が発生していたことが確認されました。このエラーの原因を調査し、サービスの状態を確認します。

---

## 🔍 確認項目

### 1. サービスの自動再起動設定

**確認ファイル**: 各プロジェクトの `docker-compose.yml`

**確認結果**:
- ✅ **nas-dashboard-monitoring**: `restart: unless-stopped` が設定されている
- ✅ **nas-dashboard**: `restart: unless-stopped` が設定されている
- ✅ **amazon-analytics**: `restart: unless-stopped` が設定されている
- ✅ **その他のサービス**: `restart: unless-stopped` が設定されている

**評価**: ✅ **全てのサービスに自動再起動設定が有効です**

---

### 2. 接続拒否エラーの原因

**エラーログの例**:
```
connect() failed (111: Connection refused) while connecting to upstream, client: 58.183.58.145, server: yoshi-nas-sys.duckdns.org, request: "GET /api/system/status HTTP/2.0", upstream: "http://192.168.68.110:9001/api/system/status"
```

**考えられる原因**:
1. **サービスが一時的に停止していた**
   - コンテナの再起動中
   - メモリ不足による強制終了
   - エラーによるクラッシュ

2. **ポートが正しく公開されていない**
   - ポートマッピングの設定ミス
   - ファイアウォールによるブロック

3. **ネットワークの問題**
   - Dockerネットワークの設定ミス
   - コンテナ間の通信問題

---

### 3. サービスの状態確認

**確認コマンド**:
```bash
# NAS環境で実行
ssh -p 23456 AdminUser@192.168.68.110

# 1. 全てのサービスの状態を確認
docker ps -a

# 2. 特定のサービスの状態を確認
docker ps | grep nas-dashboard
docker ps | grep nas-dashboard-monitoring

# 3. サービスのログを確認
docker logs nas-dashboard --tail 50
docker logs nas-dashboard-monitoring-backend-1 --tail 50

# 4. サービスの再起動履歴を確認
docker inspect nas-dashboard | grep -i restart
docker inspect nas-dashboard-monitoring-backend-1 | grep -i restart
```

---

### 4. サービスのヘルスチェック

**確認コマンド**:
```bash
# 各サービスのヘルスチェックエンドポイントにアクセス
curl http://192.168.68.110:9001/health
curl http://192.168.68.110:8002/health
curl http://192.168.68.110:5002/health
curl http://192.168.68.110:8001/health
curl http://192.168.68.110:8080/health
curl http://192.168.68.110:8111/health
```

---

## 🔧 トラブルシューティング

### 接続拒否エラーが発生する場合

1. **サービスの状態を確認**
   ```bash
   docker ps | grep <service-name>
   ```

2. **サービスのログを確認**
   ```bash
   docker logs <service-name> --tail 100
   ```

3. **サービスを再起動**
   ```bash
   docker restart <service-name>
   ```

4. **ポートが正しく公開されているか確認**
   ```bash
   docker port <service-name>
   ```

---

### サービスが頻繁に停止する場合

1. **メモリ使用量を確認**
   ```bash
   docker stats --no-stream
   ```

2. **ログを確認してエラーの原因を特定**
   ```bash
   docker logs <service-name> --tail 200
   ```

3. **リソース制限を確認**
   ```bash
   docker inspect <service-name> | grep -i memory
   ```

---

## 📊 推奨される監視項目

1. **サービスの稼働状況**
   - 定期的なヘルスチェック
   - 自動再起動の設定確認

2. **リソース使用量**
   - メモリ使用量
   - CPU使用量
   - ディスク使用量

3. **エラーログの監視**
   - 接続拒否エラーの発生頻度
   - サービスクラッシュの発生頻度

---

## 📚 参考資料

- **セキュリティ対策設定状況の確認結果**: `docs/deployment/SECURITY_STATUS_VERIFICATION.md`
- **Nginx Proxy Managerアクセスログ分析ガイド**: `docs/deployment/NGINX_ACCESS_LOG_ANALYSIS.md`
- **APIエンドポイント設定確認結果**: `docs/deployment/API_ENDPOINT_CHECK_RESULT.md`

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27

