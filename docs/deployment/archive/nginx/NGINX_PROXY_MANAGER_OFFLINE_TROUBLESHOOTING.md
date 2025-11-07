# 🔧 Nginx Proxy Manager - Offline トラブルシューティング

**作成日**: 2025-11-02  
**対象**: Nginx Proxy ManagerでProxy Hostが「Offline」と表示される問題の解決

---

## 📋 問題

Nginx Proxy ManagerでProxy Hostのステータスが「Offline」と表示される。

---

## 🔍 確認事項

### 1. 転送先サービスの状態確認

転送先のサービスが正常に動作していることを確認：

```bash
# nas-dashboardの状態確認
docker ps | grep nas-dashboard

# ポート9001へのアクセステスト
curl -I http://192.168.68.110:9001
```

**期待される結果**:
- コンテナが「Up」状態であること
- HTTP 200 OK が返ること（タイムアウトしないこと）

---

### 2. 転送先サービスのレスポンス速度確認

転送先サービスがタイムアウトしていないか確認：

```bash
# レスポンス速度をテスト
time curl -I http://192.168.68.110:9001
```

**問題がある場合**:
- レスポンスが30秒以上かかる場合、Nginx Proxy Managerのヘルスチェックがタイムアウトする可能性がある

---

### 3. Nginx Proxy Managerの設定確認

Proxy Hostの設定を確認：

1. **Nginx Proxy ManagerのWeb UIにアクセス**
   - `http://192.168.68.110:8181`

2. **Proxy Hostsタブを開く**

3. **`yoshi-nas-sys.duckdns.org`の設定を確認**:
   - **Detailsタブ**:
     - Domain Names: `yoshi-nas-sys.duckdns.org`
     - Scheme: `http`
     - Forward Hostname/IP: `192.168.68.110`
     - Forward Port: `9001`
   
   - **Custom Locationsタブ**:
     - `/`（ルート）のLocationが存在することを確認
     - Custom Locationsの設定が正しいことを確認

---

## 🔧 解決方法

### 方法1: Proxy Hostの設定を再確認

Custom Locationsを追加したことで、メインのProxy Host設定が変更された可能性があります。

**確認ポイント**:
1. **Detailsタブ**で「Forward Hostname/IP」と「Forward Port」が正しいことを確認
2. **Custom Locationsタブ**で`/`（ルート）のLocationが存在することを確認
   - 存在しない場合、追加する必要があります

---

### 方法2: Custom Locationsの設定を確認

Custom Locationsを追加した際に、メインのLocation（`/`）が削除された可能性があります。

**解決方法**:
1. **Custom Locationsタブを開く**
2. **`/`（ルート）のLocationが存在することを確認**
3. **存在しない場合、追加する**:
   - 「Add Location」をクリック
   - Define location: `/`
   - Scheme: `http`
   - Forward Hostname/IP: `192.168.68.110`
   - Forward Port: `9001`
4. **「Save」をクリック**

---

### 方法3: Proxy Hostを再起動

Nginx Proxy Managerの設定を再読み込み：

1. **Proxy Hostsタブを開く**
2. **`yoshi-nas-sys.duckdns.org`の設定を開く**
3. **「Save」をクリック**（設定を再保存してNginxを再読み込み）

---

### 方法4: Nginx Proxy Managerコンテナを再起動

Nginx Proxy Managerコンテナを再起動して設定を再読み込み：

```bash
docker restart nginx-proxy-manager
```

---

### 方法5: 転送先サービスのパフォーマンス改善

転送先サービス（nas-dashboard）のレスポンス速度が遅い場合、パフォーマンスを改善：

1. **nas-dashboardコンテナのログを確認**:
   ```bash
   docker logs nas-dashboard --tail 50
   ```

2. **エラーや警告がないか確認**

3. **必要に応じてコンテナを再起動**:
   ```bash
   docker restart nas-dashboard
   ```

---

## ⚠️ 注意事項

### Custom Locationsを追加した際の注意点

Custom Locationsを追加した際に、メインのProxy Host設定（Detailsタブ）の「Forward Hostname/IP」と「Forward Port」が空になっている可能性があります。

**確認すべき項目**:
1. **Detailsタブ**の設定が正しいことを確認
2. **Custom Locationsタブ**で`/`（ルート）のLocationが存在することを確認

---

## ✅ 確認チェックリスト

- [ ] nas-dashboardコンテナが起動している
- [ ] ポート9001にアクセス可能（HTTP 200 OK）
- [ ] レスポンスが30秒以内（タイムアウトしない）
- [ ] Proxy HostのDetailsタブの設定が正しい
- [ ] Custom Locationsタブで`/`（ルート）のLocationが存在する
- [ ] Nginx Proxy Managerコンテナが起動している
- [ ] Nginx Proxy Managerのログにエラーがない

---

## 🔍 詳細なデバッグ

### Nginx Proxy Managerのログを確認

```bash
docker logs nginx-proxy-manager --tail 100 | grep -i error
```

### 転送先サービスのログを確認

```bash
docker logs nas-dashboard --tail 50
```

### ネットワーク接続を確認

```bash
# Nginx Proxy Managerコンテナから転送先への接続をテスト
docker exec nginx-proxy-manager curl -I http://192.168.68.110:9001
```

---

## 📝 まとめ

「Offline」と表示される主な原因：

1. **転送先サービスが停止している**
2. **転送先サービスのレスポンスが遅すぎる（タイムアウト）**
3. **Proxy Hostの設定が正しくない**（Custom Locationsを追加した際に設定が変更された）
4. **Custom Locationsで`/`（ルート）のLocationが削除された**

**解決手順**:
1. 転送先サービスの状態を確認
2. Proxy Hostの設定を確認（DetailsタブとCustom Locationsタブ）
3. 必要に応じて設定を修正して再保存
4. Nginx Proxy Managerコンテナを再起動

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

