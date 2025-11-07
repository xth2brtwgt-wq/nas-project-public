# 🔍 Nginx Proxy Manager - 設定ファイル確認（修正版）

**作成日**: 2025-11-02  
**目的**: Nginx Proxy Managerの設定ファイルを正しく確認する方法

---

## 🔍 設定確認手順（修正版）

### ステップ1: NAS環境にSSH接続

```bash
ssh -p 23456 AdminUser@192.168.68.110
```

### ステップ2: Nginx Proxy Managerのコンテナ名を確認

```bash
docker ps | grep nginx-proxy-manager
```

### ステップ3: 設定ファイルの場所を確認

```bash
docker exec nginx-proxy-manager ls -la /data/nginx/proxy_host/
```

### ステップ4: meetings関連の設定を確認（方法1: ファイル名を指定）

```bash
# 設定ファイルの一覧を確認
docker exec nginx-proxy-manager sh -c "ls /data/nginx/proxy_host/*.conf"

# 各ファイルを確認
docker exec nginx-proxy-manager sh -c "cat /data/nginx/proxy_host/*.conf" | grep -A 20 "meetings"
```

### ステップ5: meetings関連の設定を確認（方法2: 直接検索）

```bash
# すべての設定ファイルの内容を確認
docker exec nginx-proxy-manager sh -c "grep -r 'meetings' /data/nginx/proxy_host/" 

# または、より詳細に
docker exec nginx-proxy-manager sh -c "find /data/nginx/proxy_host/ -name '*.conf' -exec grep -l 'meetings' {} \;"
```

### ステップ6: 全体の設定を確認

```bash
# すべての設定ファイルの内容を確認
docker exec nginx-proxy-manager sh -c "cat /data/nginx/proxy_host/*.conf" | less
```

---

## 🐛 トラブルシューティング

### 設定ファイルが見つからない場合

1. **Nginx Proxy Managerのデータディレクトリを確認**:

```bash
docker exec nginx-proxy-manager ls -la /data/nginx/
```

2. **Nginx Proxy Managerのボリュームマウントを確認**:

```bash
docker inspect nginx-proxy-manager | grep -A 10 "Mounts"
```

### Advancedタブの設定が反映されていない場合

1. **Proxy Hostを再保存**:
   - Nginx Proxy ManagerのWeb UIで、Proxy Hostを編集
   - 「Details」タブ → 「Save」
   - 「Advanced」タブ → 「Save」

2. **Nginx設定を再読み込み**:

```bash
docker exec nginx-proxy-manager nginx -t  # 設定ファイルの構文チェック
docker exec nginx-proxy-manager nginx -s reload  # 設定を再読み込み
```

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant


