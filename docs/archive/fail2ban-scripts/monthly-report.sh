#!/bin/bash

MONTH=$(date +%Y-%m)

# レポート内容を生成
REPORT_CONTENT=$(cat << REPORT
===================================================
Fail2ban 月次セキュリティサマリー
月: $MONTH
作成日時: $(date '+%Y-%m-%d %H:%M:%S')
===================================================

【現在のセキュリティ状況】
$(sudo docker exec fail2ban fail2ban-client status sshd 2>/dev/null)

【BAN中のIP一覧】
$(sudo docker exec fail2ban fail2ban-client get sshd banip 2>/dev/null)

【過去30日間のBAN実行（最新50件）】
$(sudo docker logs fail2ban --since 30d 2>&1 | grep "Ban " | tail -50)

【月間統計】
今月のBAN実行回数: $(sudo docker logs fail2ban --since 30d 2>&1 | grep -c "Ban ") 回

【攻撃元TOP5】
$(sudo docker logs fail2ban --since 30d 2>&1 | grep "Ban " | awk '{print $NF}' | sort | uniq -c | sort -rn | head -5)

===================================================
サマリー終了
===================================================
REPORT
)

# コンテナ内にレポートファイル作成
echo "$REPORT_CONTENT" | sudo docker exec -i fail2ban tee /tmp/monthly-report.txt > /dev/null

echo "月次サマリー生成完了"

# メール送信
sudo docker exec fail2ban python3 /data/scripts/send-monthly-report.py

if [ $? -eq 0 ]; then
    echo "✓ メール送信成功"
else
    echo "✗ メール送信失敗"
    # デバッグ: レポート内容確認
    sudo docker exec fail2ban cat /tmp/monthly-report.txt
fi
