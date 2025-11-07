# ✅ 認証モジュール（auth_common.py）更新のデプロイ

**作成日**: 2025-11-04  
**目的**: `auth_common.py`の修正を各サービスに反映

---

## 📋 更新内容

`nas-dashboard/utils/auth_common.py`の`get_dashboard_login_url()`関数を簡略化：

- **変更前**: リクエストのヘッダーから外部アクセスを判定
- **変更後**: 常に外部URL（`https://yoshi-nas-sys.duckdns.org:8443/login`）を返す

---

## ✅ デプロイ手順

### 重要: マウントされているため再ビルド不要

`auth_common.py`は各サービスコンテナ内にマウントされているため、コンテナを再起動するだけで最新のコードが反映されます。

### 各サービスの再起動

```bash
# 1. nas-dashboard（認証モジュールのソース）
cd ~/nas-project/nas-dashboard
git pull origin feature/monitoring-fail2ban-integration
sudo docker compose restart nas-dashboard

# 2. youtube-to-notion
cd ~/nas-project/youtube-to-notion
git pull origin feature/monitoring-fail2ban-integration
sudo docker compose restart youtube-to-notion

# 3. amazon-analytics
cd ~/nas-project/amazon-analytics
git pull origin feature/monitoring-fail2ban-integration
sudo docker compose restart web

# 4. document-automation
cd ~/nas-project/document-automation
git pull origin feature/monitoring-fail2ban-integration
sudo docker compose restart web

# 5. nas-dashboard-monitoring
cd ~/nas-project/nas-dashboard-monitoring
git pull origin feature/monitoring-fail2ban-integration
sudo docker compose restart backend

# 6. meeting-minutes-byc
cd ~/nas-project/meeting-minutes-byc
git pull origin feature/monitoring-fail2ban-integration
sudo docker compose restart meeting-minutes-byc
```

---

## 📝 クイックコマンド（一括実行）

```bash
# 各サービスを順番に再起動
for service_dir in nas-dashboard youtube-to-notion amazon-analytics document-automation nas-dashboard-monitoring meeting-minutes-byc; do
    echo "=== $service_dir ==="
    cd ~/nas-project/$service_dir
    git pull origin feature/monitoring-fail2ban-integration
    if [ "$service_dir" = "nas-dashboard" ]; then
        sudo docker compose restart nas-dashboard
    elif [ "$service_dir" = "amazon-analytics" ] || [ "$service_dir" = "document-automation" ]; then
        sudo docker compose restart web
    elif [ "$service_dir" = "nas-dashboard-monitoring" ]; then
        sudo docker compose restart backend
    else
        sudo docker compose restart $service_dir
    fi
    echo ""
done
```

---

## 🔍 確認手順

### 各サービスでログを確認

```bash
# 1. youtube-to-notion
cd ~/nas-project/youtube-to-notion
sudo docker compose logs youtube-to-notion | grep -i "\[AUTH\]" | tail -5

# 2. amazon-analytics
cd ~/nas-project/amazon-analytics
sudo docker compose logs web | grep -i "\[AUTH\]" | tail -5

# 3. document-automation
cd ~/nas-project/document-automation
sudo docker compose logs web | grep -i "\[AUTH\]" | tail -5

# 4. nas-dashboard-monitoring
cd ~/nas-project/nas-dashboard-monitoring
sudo docker compose logs backend | grep -i "\[AUTH\]" | tail -5

# 5. meeting-minutes-byc
cd ~/nas-project/meeting-minutes-byc
sudo docker compose logs meeting-minutes-byc | grep -i "\[AUTH\]" | tail -5
```

**期待されるログ**:
```
[AUTH] ログインURL: https://yoshi-nas-sys.duckdns.org:8443/login
[AUTH] 認証が必要です: / -> https://yoshi-nas-sys.duckdns.org:8443/login
```

### 外部からアクセスして確認

```bash
# 各サービスに直接アクセス（認証なし）
curl -v https://yoshi-nas-sys.duckdns.org:8443/youtube
curl -v https://yoshi-nas-sys.duckdns.org:8443/analytics
curl -v https://yoshi-nas-sys.duckdns.org:8443/documents
curl -v https://yoshi-nas-sys.duckdns.org:8443/monitoring
curl -v https://yoshi-nas-sys.duckdns.org:8443/meetings
```

**期待される結果**:
```
< HTTP/2 302 または 307
< Location: https://yoshi-nas-sys.duckdns.org:8443/login
```

---

## ⚠️ 注意事項

### マウントされているため再ビルド不要

`auth_common.py`は各サービスコンテナ内に以下のようにマウントされています：

```yaml
volumes:
  - /home/AdminUser/nas-project/nas-dashboard:/nas-project/nas-dashboard:ro
```

そのため、コンテナを再起動するだけで最新のコードが反映されます。再ビルドは不要です。

### Pythonのモジュールキャッシュ

Pythonは一度インポートしたモジュールをキャッシュするため、コンテナを再起動する必要があります。

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

