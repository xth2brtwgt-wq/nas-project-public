# 🔍 Nginx Proxy Manager - 設定ファイル確認（NAS環境）

**作成日**: 2025-11-02  
**目的**: NAS環境でNginx Proxy Managerの設定ファイルを確認する方法

---

## 🔍 設定確認手順（NAS環境）

### ステップ1: NAS環境にSSH接続

```bash
ssh -p 23456 AdminUser@192.168.68.110
```

### ステップ2: 設定ファイルの場所を確認

```bash
# 設定ファイルの一覧を確認
docker exec nginx-proxy-manager ls /data/nginx/proxy_host/

# または、findコマンドを使用
docker exec nginx-proxy-manager find /data/nginx/proxy_host/ -name "*.conf"
```

### ステップ3: meetings関連の設定を確認

```bash
# 方法1: すべての設定ファイルから検索
docker exec nginx-proxy-manager sh -c "cat /data/nginx/proxy_host/*.conf" | grep -A 20 "meetings"

# 方法2: 各ファイルを個別に確認
docker exec nginx-proxy-manager sh -c "for file in /data/nginx/proxy_host/*.conf; do echo \"=== \$file ===\"; cat \"\$file\" | grep -A 20 'meetings'; done"

# 方法3: ファイル名を指定して確認
docker exec nginx-proxy-manager sh -c "ls /data/nginx/proxy_host/*.conf" | while read file; do
  echo "=== $file ==="
  docker exec nginx-proxy-manager cat "$file" | grep -A 20 "meetings"
done
```

### ステップ4: Advancedタブの設定を確認

```bash
# location ~ ^/meetings/static/ の設定があるか確認
docker exec nginx-proxy-manager sh -c "cat /data/nginx/proxy_host/*.conf" | grep -B 5 -A 10 "meetings/static"

# rewrite の設定があるか確認
docker exec nginx-proxy-manager sh -c "cat /data/nginx/proxy_host/*.conf" | grep -B 5 -A 5 "meetings/static.*rewrite"
```

### ステップ5: 全体の設定を確認

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

## 📝 確認すべき内容

1. `location ~ ^/meetings/static/` の設定が含まれているか
2. `rewrite ^/meetings/static/(.*)$ /static/$1 break;` が含まれているか
3. `proxy_pass http://192.168.68.110:5002;` が含まれているか

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant


