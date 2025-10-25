#!/bin/bash

WEEK_NUM=$(date +%Y-W%V)

# レポート内容を生成
REPORT_CONTENT=$(cat << REPORT
===================================================
Fail2ban 週次セキュリティレポート
週: $WEEK_NUM
作成日時: $(date '+%Y-%m-%d %H:%M:%S')
===================================================

【現在のセキュリティ状況】
$(sudo docker exec fail2ban fail2ban-client status sshd 2>/dev/null)

【BAN中のIP一覧】
$(sudo docker exec fail2ban fail2ban-client get sshd banip 2>/dev/null)

【過去7日間のBAN実行】
$(sudo docker logs fail2ban --since 7d 2>&1 | grep "Ban " | tail -20)

【統計】
今週のBAN実行回数: $(sudo docker logs fail2ban --since 7d 2>&1 | grep -c "Ban ") 回

===================================================
レポート終了
===================================================
REPORT
)

# コンテナ内にレポートファイル作成
echo "$REPORT_CONTENT" | sudo docker exec -i fail2ban tee /tmp/weekly-report.txt > /dev/null

echo "週次レポート生成完了"

# メール送信
sudo docker exec fail2ban python3 /data/scripts/send-weekly-report.py

if [ $? -eq 0 ]; then
    echo "✓ メール送信成功"
else
    echo "✗ メール送信失敗"
    # デバッグ: レポート内容確認
    sudo docker exec fail2ban cat /tmp/weekly-report.txt
fi
