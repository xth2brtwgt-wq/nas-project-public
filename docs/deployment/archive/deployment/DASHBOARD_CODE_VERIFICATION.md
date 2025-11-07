# ダッシュボードコード確認手順

## コンテナ内のコードを確認する方法

### 1. コンテナ内のapp.pyを確認
```bash
sudo docker exec nas-dashboard cat /app/app.py | grep -A 10 "def get_base_url"
```

### 2. get_base_url()関数の確認ポイント
以下のコードが含まれているか確認：
- `forwarded_scheme = 'https'` (外部アクセス時)
- `if 'yoshi-nas-sys.duckdns.org' in host:` の条件分岐

### 3. get_dynamic_services()関数の確認ポイント
以下のコードが含まれているか確認：
- `if is_external_access:` の条件分岐
- `scheme = 'https'` (外部アクセス時)

### 4. コンテナを完全に再ビルドする場合
```bash
cd ~/nas-project/nas-dashboard
git pull origin feature/monitoring-fail2ban-integration
sudo docker compose down
sudo docker compose build --no-cache
sudo docker compose up -d
```

### 5. 確認コマンド一覧
```bash
# get_base_url()関数の確認
sudo docker exec nas-dashboard grep -A 15 "def get_base_url" /app/app.py | head -20

# forwarded_scheme = 'https' の確認
sudo docker exec nas-dashboard grep "forwarded_scheme = 'https'" /app/app.py

# get_dynamic_services()関数の確認
sudo docker exec nas-dashboard grep -A 20 "def get_dynamic_services" /app/app.py | head -25

# scheme = 'https' の確認
sudo docker exec nas-dashboard grep -A 5 "if is_external_access:" /app/app.py

# デバッグログの確認
sudo docker exec nas-dashboard grep "\[DASHBOARD\]" /app/app.py
```

