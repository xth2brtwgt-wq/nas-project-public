# 🔍 Nginx Proxy Manager - 設定確認方法

**作成日**: 2025-11-02  
**目的**: Nginx Proxy Managerの設定が正しく反映されているか確認する方法

---

## 🔍 設定確認手順

### ステップ1: Nginx Proxy Managerの設定ファイルを確認

1. **NAS環境にSSH接続**:

```bash
ssh -p 23456 AdminUser@192.168.68.110
```

2. **Nginx Proxy Managerの設定ファイルを確認**:

```bash
# Nginx Proxy Managerのコンテナ名を確認
docker ps | grep nginx-proxy-manager

# 設定ファイルの場所を確認
docker exec nginx-proxy-manager ls -la /data/nginx/proxy_host/

# yoshi-nas-sys.duckdns.orgの設定ファイルを確認
docker exec nginx-proxy-manager cat /data/nginx/proxy_host/*.conf | grep -A 20 "meetings"
```

### ステップ2: Advancedタブの設定を確認

1. **Nginx Proxy ManagerのWeb UI**: `http://192.168.68.110:8181`

2. **「Proxy Hosts」タブ → `yoshi-nas-sys.duckdns.org`を編集**

3. **「Advanced」タブをクリック**

4. **「Custom Nginx Configuration」の内容を確認**

以下の設定が含まれているか確認：

```nginx
location ~ ^/meetings/static/(.*)$ {
    rewrite ^/meetings/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:5002;
    ...
}
```

### ステップ3: Nginx設定の再読み込み

設定を変更した後、Nginxが設定を再読み込みしているか確認：

```bash
# Nginx Proxy Managerのログを確認
docker logs nginx-proxy-manager --tail 50 | grep -i "reload\|error"
```

---

## 🐛 トラブルシューティング

### 設定が反映されていない場合

1. **Proxy Hostを再保存**:
   - 「Details」タブ → 「Save」
   - 「Advanced」タブ → 「Save」

2. **Nginx Proxy Managerを再起動**:

```bash
docker restart nginx-proxy-manager
```

### locationの優先順位の問題

Nginxは最初にマッチした`location`を使用します。Custom Locationの`/meetings`が先にマッチしている可能性があります。

**解決方法**: Advancedタブの`location`ブロックを**より具体的に**記述します：

```nginx
# より具体的なlocation（先にマッチさせる）
location ~ ^/meetings/static/(.*)$ {
    rewrite ^/meetings/static/(.*)$ /static/$1 break;
    proxy_pass http://192.168.68.110:5002;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant


