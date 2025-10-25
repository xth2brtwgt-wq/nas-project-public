#!/usr/bin/env python3
import smtplib
import sys
from email.mime.text import MIMEText
from datetime import datetime

ip = sys.argv[1] if len(sys.argv) > 1 else "unknown"
jail = sys.argv[2] if len(sys.argv) > 2 else "unknown"

body = f"""IP {ip} has been banned from jail '{jail}'

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Hostname: DXP2800
"""

msg = MIMEText(body)
msg['Subject'] = f'[NAS Security] {jail}: banned {ip}'
msg['From'] = 'mipatago.netsetting@gmail.com'
msg['To'] = 'mipatago.netsetting@gmail.com'

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('mipatago.netsetting@gmail.com', 'bpio kqxc pvqv sgyd')
    server.send_message(msg)
    server.quit()
    print(f"Mail sent for {ip}")
except Exception as e:
    print(f"Mail failed: {e}")
    sys.exit(1)
