### 監視セットアップ手順（URL一覧生成 + ヘルスチェック定期実行）

対象: `/home/AdminUser/nas-project` リポジトリ

1) 稼働URL一覧を生成（稼働中コンテナのみ対象）
```bash
cd /home/AdminUser/nas-project
python3 scripts/generate_running_service_urls.py
cat docs/SERVICE_URLS.md
```

2) ヘルスチェックを実行（結果は `docs/HEALTH_STATUS.md`）
```bash
python3 scripts/monitor_health.py
cat docs/HEALTH_STATUS.md
```

3) 定期実行（cron）
```bash
crontab -e
# 5分ごとにURL更新（稼働中のみ）とヘルスチェック実行（ログは統合データディレクトリへ）
*/5 * * * * cd /home/AdminUser/nas-project && /usr/bin/python3 scripts/generate_running_service_urls.py && /usr/bin/python3 scripts/monitor_health.py >/home/AdminUser/nas-project-data/system-monitoring/logs/monitoring_cron.log 2>&1
```

4) systemd timer（任意、cronの代替）
```bash
sudo tee /etc/systemd/system/nas-monitoring.service >/dev/null <<'UNIT'
[Unit]
Description=NAS projects health monitoring

[Service]
Type=oneshot
WorkingDirectory=/home/AdminUser/nas-project
ExecStart=/usr/bin/python3 scripts/generate_service_urls.py
ExecStart=/usr/bin/python3 scripts/generate_running_service_urls.py
ExecStart=/usr/bin/python3 scripts/monitor_health.py
UNIT

sudo tee /etc/systemd/system/nas-monitoring.timer >/dev/null <<'UNIT'
[Unit]
Description=Run NAS projects health monitoring every 5 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
Unit=nas-monitoring.service

[Install]
WantedBy=timers.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable --now nas-monitoring.timer
sudo systemctl list-timers | grep nas-monitoring
```

補足
- `docker-compose.yml` の `version:` は削除済み（Compose V2推奨）。
- `docs/service_urls.json` は監視スクリプト用の機械可読ファイルです。
- 監視の閾値/対象エンドポイントは `scripts/monitor_health.py` で `/health` → `/docs` → `/` の順にチェックします。


