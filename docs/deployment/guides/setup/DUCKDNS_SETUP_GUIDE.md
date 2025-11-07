# 🦆 DuckDNS設定ガイド

**作成日**: 2025-01-27  
**対象**: 外部アクセス設定（HTTPS化の前提条件）

---

## 📋 概要

DuckDNSは無料のDynamic DNS（DDNS）サービスです。外部IPアドレスが変わっても、同じドメイン名でアクセスできるようになります。

**メリット:**
- 完全無料
- 設定が簡単
- HTTPS証明書取得に必要なドメイン名を提供

---

## 🚀 ステップ1: DuckDNSアカウントの作成

### 1-1. DuckDNSのWebサイトにアクセス

1. ブラウザで https://www.duckdns.org/ を開く
2. 右上の「Sign in with GitHub」または「Sign in with Google」をクリック

### 1-2. アカウント登録

**GitHub経由の場合:**
- GitHubアカウントでログイン
- DuckDNSへのアクセス許可を承認

**Google経由の場合:**
- Googleアカウントでログイン
- DuckDNSへのアクセス許可を承認

### 1-3. ログイン確認

- ログイン後、DuckDNSのダッシュボードが表示されます
- 左側にメニューがあります

---

## 🚀 ステップ2: ドメイン名の選択と作成

### 2-1. ドメイン名を選択

1. DuckDNSダッシュボードで「Add Domain」をクリック
2. ドメイン名を入力（例: `nas-project`）
   - 注意: 利用可能かどうか自動チェックされます
   - 利用不可の場合は別の名前を試してください
3. ドメイン名は以下の形式になります:
   ```
   [選択した名前].duckdns.org
   例: nas-project → nas-project.duckdns.org
   ```

### 2-2. ドメインの確認

- 作成後、ドメインリストに表示されます
- 例: `nas-project.duckdns.org`

---

## 🚀 ステップ3: 外部IPアドレスの設定

### 3-1. 現在の外部IPアドレスを確認

**ローカル（Mac）から確認:**
```bash
curl ifconfig.me
# または
curl ipinfo.io/ip
```

**例:**
```
123.45.67.89
```

### 3-2. DuckDNSにIPアドレスを設定

#### 方法A: Webダッシュボードから設定（手動更新）

1. DuckDNSダッシュボードで作成したドメインを確認
2. 「IP」欄に現在の外部IPアドレスを入力
3. 「Update IP」ボタンをクリック
4. 成功メッセージが表示されます

#### 方法B: APIを使用して自動更新（推奨）

DuckDNSにはAPI経由でIPアドレスを自動更新する機能があります。

1. **トークンの取得**
   - DuckDNSダッシュボードで「Token」を確認
   - このトークンは後で使用します（重要: 他人に見せない）

2. **APIでIP更新**
   ```bash
   # 現在の外部IPを取得してDuckDNSに更新
   curl "https://www.duckdns.org/update?domains=nas-project&token=your-token&ip="
   
   # IPを自動検出して更新する場合
   curl "https://www.duckdns.org/update?domains=nas-project&token=your-token&ip=$(curl -s ifconfig.me)"
   ```

### 3-3. 自動更新スクリプトの作成（推奨）

外部IPが変わったときに自動で更新するスクリプトを作成します。

#### NAS上で自動更新スクリプトを作成

```bash
# NASにSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# スクリプトを作成
sudo nano /usr/local/bin/duckdns-update.sh
```

#### スクリプト内容

```bash
#!/bin/bash
# DuckDNS IP更新スクリプト

# 設定（以下を実際の値に置き換えてください）
DOMAIN="nas-project"  # ドメイン名（.duckdns.orgは不要）
TOKEN="your-token-here"  # DuckDNSのトークン

# 現在の外部IPを取得
CURRENT_IP=$(curl -s ifconfig.me)

# DuckDNSにIPを更新
RESPONSE=$(curl -s "https://www.duckdns.org/update?domains=${DOMAIN}&token=${TOKEN}&ip=${CURRENT_IP}")

# 結果をログに記録
echo "$(date): DuckDNS IP update: ${RESPONSE}" >> /var/log/duckdns-update.log
```

#### スクリプトに実行権限を付与

```bash
sudo chmod +x /usr/local/bin/duckdns-update.sh

# テスト実行
sudo /usr/local/bin/duckdns-update.sh

# ログを確認
tail /var/log/duckdns-update.log
```

#### cronで定期実行を設定

```bash
# cron設定を編集
sudo crontab -e

# 以下の行を追加（毎日1回、午前3時に実行）
0 3 * * * /usr/local/bin/duckdns-update.sh

# または、外部IP変更を検出して自動更新する場合
# */5 * * * * /usr/local/bin/duckdns-update.sh  # 5分ごと
```

---

## 🚀 ステップ4: ドメインが正しく設定されているか確認

### 4-1. DNS解決の確認

**ローカル（Mac）から確認:**
```bash
# nslookupで確認
nslookup nas-project.duckdns.org

# digで確認
dig nas-project.duckdns.org

# 期待される結果:
# nas-project.duckdns.org のIPアドレスが、現在の外部IPと一致している
```

### 4-2. ブラウザで確認

1. ブラウザで `http://nas-project.duckdns.org:9001` にアクセス（まだHTTPSではない）
2. NASのダッシュボードが表示されれば成功

**注意:** ドメイン設定の反映には数分かかる場合があります

---

## ⚙️ トラブルシューティング

### ドメインが外部IPを指していない

**原因:**
- DNSキャッシュ
- DuckDNSの設定が未更新

**対処法:**
```bash
# DNSキャッシュをクリア（Macの場合）
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder

# 再度確認
nslookup nas-project.duckdns.org
```

### 自動更新が動作しない

**確認事項:**
1. トークンが正しいか確認
2. スクリプトに実行権限があるか確認
   ```bash
   ls -l /usr/local/bin/duckdns-update.sh
   ```
3. cronジョブが正しく設定されているか確認
   ```bash
   sudo crontab -l
   ```
4. ログを確認
   ```bash
   tail -20 /var/log/duckdns-update.log
   ```

---

## 📝 チェックリスト

- [ ] DuckDNSアカウント作成完了
- [ ] ドメイン名を選択・作成完了（例: `nas-project.duckdns.org`）
- [ ] 外部IPアドレスをDuckDNSに設定完了
- [ ] DNS解決の確認完了（nslookup/dig）
- [ ] 自動更新スクリプト作成（オプション）
- [ ] 自動更新のcron設定（オプション）

---

## 🔐 セキュリティ注意事項

### トークンの保護

- **DuckDNSのトークンは秘密情報です**
- 他人に教えない
- Gitリポジトリにコミットしない（`.gitignore`に追加）
- スクリプトファイルの権限を適切に設定

```bash
# スクリプトファイルの権限を制限
sudo chmod 600 /usr/local/bin/duckdns-update.sh
```

### 環境変数の使用（より安全な方法）

トークンをスクリプトに直接書くのではなく、環境変数や設定ファイルに保存:

```bash
# 設定ファイルを作成
sudo nano /etc/duckdns.conf
```

```bash
DOMAIN=nas-project
TOKEN=your-token-here
```

```bash
# スクリプトを修正して設定ファイルを読み込む
source /etc/duckdns.conf
```

---

## 📚 次のステップ

DuckDNS設定が完了したら:

1. **HTTPS証明書の取得**
   - `docs/deployment/HTTPS_SETUP_GUIDE.md` を参照
   - Let's Encryptで証明書を取得

2. **nginxの設定**
   - HTTPS設定を行い、証明書を使用

---

## 📚 参考資料

- **DuckDNS公式サイト**: https://www.duckdns.org/
- **DuckDNS API ドキュメント**: https://www.duckdns.org/spec.jsp

---

**作成日**: 2025-01-27  
**更新日**: 2025-01-27  
**作成者**: AI Assistant


