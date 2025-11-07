# ダッシュボードURLスキーム修正手順

## 問題
ダッシュボードのサービスリンクが`http://`になっている（`https://`であるべき）

## 修正内容
1. `get_base_url()`で`X-Forwarded-Proto`ヘッダーを確認
2. `get_dynamic_services()`で外部アクセスの場合は常に`https`スキームを使用

## デプロイ手順

### 1. 最新コードを取得
```bash
cd ~/nas-project/nas-dashboard
git pull origin feature/monitoring-fail2ban-integration
```

### 2. コンテナを完全に再起動
```bash
sudo docker compose down
sudo docker compose up -d
```

### 3. ログを確認
```bash
sudo docker logs -f nas-dashboard | grep "\[URL\]"
```

ブラウザでダッシュボードにアクセスすると、以下のようなログが表示されるはずです：
```
[URL] get_base_url() = https://yoshi-nas-sys.duckdns.org:8443
[URL] hostname = yoshi-nas-sys.duckdns.org, current_port = 8443
[URL] is_external_access = True
[URL] scheme = https (is_external_access = True)
[URL] nas_monitoring -> https://yoshi-nas-sys.duckdns.org:8443/monitoring (external)
```

### 4. ブラウザのキャッシュをクリア
- **Chrome/Edge**: `Ctrl+Shift+Delete` (Windows) または `Cmd+Shift+Delete` (Mac)
- **Safari**: `Cmd+Option+E` (キャッシュをクリア)
- または、シークレット/プライベートモードでアクセス

### 5. ダッシュボードページを強制リロード
- **Chrome/Edge**: `Ctrl+Shift+R` (Windows) または `Cmd+Shift+R` (Mac)
- **Safari**: `Cmd+Option+R`

### 6. HTMLソースを確認
ブラウザの開発者ツール（F12）で以下を確認：
- 「NAS監視システム」ボタンの`href`属性が`https://yoshi-nas-sys.duckdns.org:8443/monitoring`になっているか

## 確認ポイント
- すべてのサービスURLが`https://`で始まること
- ログに`[URL] scheme = https`が表示されること
- ログに`[URL] is_external_access = True`が表示されること

## トラブルシューティング
もし`http`スキームが表示され続ける場合：

1. **コンテナが最新コードで実行されているか確認**
   ```bash
   sudo docker exec nas-dashboard cat /app/app.py | grep "scheme = 'https'"
   ```

2. **ログでURL生成が実行されているか確認**
   ```bash
   sudo docker logs nas-dashboard --tail 100 | grep "\[URL\]"
   ```

3. **完全に再ビルド**
   ```bash
   sudo docker compose down
   sudo docker compose build --no-cache
   sudo docker compose up -d
   ```

