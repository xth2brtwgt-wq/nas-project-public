# ✅ 外部アクセス時のリダイレクトURLテスト

**作成日**: 2025-11-04  
**目的**: 外部アクセス時に外部URLにリダイレクトされるかテスト

---

## 🔍 テスト手順

### ステップ1: 外部からアクセス（curl）

```bash
# 外部からアクセス（Nginx Proxy Manager経由）
curl -v https://yoshi-nas-sys.duckdns.org:8443/analytics/
```

**期待される結果**:
```
< HTTP/1.1 307 Temporary Redirect
< Location: https://yoshi-nas-sys.duckdns.org:8443/login
```

### ステップ2: ログを確認

```bash
cd ~/nas-project/amazon-analytics

# 認証関連のログを確認（リクエスト後）
sudo docker compose logs web | grep -i "\[AUTH\]" | tail -20

# 最新のアクセスログを確認
sudo docker compose logs web --tail 50 | grep -i "GET\|POST\|認証\|auth"
```

**期待されるログ**:
```
[AUTH] X-Forwarded-Host: yoshi-nas-sys.duckdns.org:8443
[AUTH] Host: ...
[AUTH] X-Forwarded-Proto: https
[AUTH] ホスト名: yoshi-nas-sys.duckdns.org:8443, 外部アクセス判定: True
[AUTH] 外部アクセスを検出。ログインURL: https://yoshi-nas-sys.duckdns.org:8443/login
[AUTH] 認証が必要です: / -> https://yoshi-nas-sys.duckdns.org:8443/login
```

### ステップ3: 内部からアクセス（比較）

```bash
# 内部からアクセス（直接ポート）
curl -v http://192.168.68.110:8001/
```

**期待される結果**:
```
< HTTP/1.1 307 Temporary Redirect
< Location: http://192.168.68.110:9001/login
```

**期待されるログ**:
```
[AUTH] Host: 192.168.68.110:8001
[AUTH] ホスト名: 192.168.68.110:8001, 外部アクセス判定: False
[AUTH] 内部アクセスを検出。ログインURL: http://192.168.68.110:9001/login
```

---

## 🔧 ログレベルをDEBUGに設定（必要に応じて）

ログが表示されない場合、`auth_common.py`のログレベルを確認してください：

```bash
# コンテナ内でログレベルを確認
sudo docker compose exec web python -c "
import logging
from pathlib import Path
import sys
sys.path.insert(0, '/nas-project/nas-dashboard')
from utils import auth_common
print(f'ログレベル: {auth_common.logger.level}')
print(f'DEBUGレベル: {logging.DEBUG}')
"
```

---

## 📝 トラブルシューティング

### X-Forwarded-Hostヘッダーが設定されていない場合

Nginx Proxy Managerの設定を確認：

1. **Proxy Host設定**:
   - `X-Forwarded-Host`ヘッダーが自動的に設定されているか確認
   - Advancedタブでカスタムヘッダーが設定されているか確認

2. **Nginx設定ファイルを確認**:
   ```bash
   # Nginx設定ファイルを確認（Nginx Proxy Managerのコンテナ内）
   sudo docker exec nginx-proxy-manager cat /etc/nginx/conf.d/default.conf | grep -i "forwarded"
   ```

### ログが表示されない場合

1. **リクエストが実際に送信されているか確認**:
   ```bash
   # アクセスログ全体を確認
   sudo docker compose logs web --tail 100
   ```

2. **ログレベルをDEBUGに設定**:
   - `auth_common.py`の`logger.debug`が実行されるように確認

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

