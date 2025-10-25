#!/usr/bin/env python3
import smtplib
import sys
from email.mime.text import MIMEText

report_file = sys.argv[1] if len(sys.argv) > 1 else '/tmp/monthly-report.txt'

with open(report_file, 'r') as f:
    body = f.read()

msg = MIMEText(body)
msg['Subject'] = '[NAS Security] Monthly Security Summary'
msg['From'] = 'mipatago.netsetting@gmail.com'
msg['To'] = 'mipatago.netsetting@gmail.com'

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('mipatago.netsetting@gmail.com', 'bpio kqxc pvqv sgyd')
    server.send_message(msg)
    server.quit()
    print('Monthly report sent successfully')
except Exception as e:
    print(f'Mail failed: {e}')
    sys.exit(1)
