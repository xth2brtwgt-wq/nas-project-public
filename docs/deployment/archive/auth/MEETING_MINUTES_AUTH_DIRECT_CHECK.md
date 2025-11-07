# 🔍 Meeting Minutes BYC 認証 直接確認手順

**作成日**: 2025-11-04  
**目的**: コンテナ内の実際のパスと認証状態を確認

---

## 🔍 確認手順

### ステップ1: コンテナ内のパス確認

```bash
cd ~/nas-project/meeting-minutes-byc
sudo docker compose exec meeting-minutes-byc bash -c "
echo '1. 作業ディレクトリ:'
pwd

echo ''
echo '2. app.pyの場所:'
find /app -name app.py 2>/dev/null || echo 'app.pyが見つかりません'

echo ''
echo '3. /nas-project のマウント確認:'
ls -la /nas-project 2>/dev/null || echo '/nas-project が見つかりません'

echo ''
echo '4. /nas-project/nas-dashboard のマウント確認:'
ls -la /nas-project/nas-dashboard 2>/dev/null || echo '/nas-project/nas-dashboard が見つかりません'

echo ''
echo '5. /nas-project/nas-dashboard/utils/auth_common.py の確認:'
ls -la /nas-project/nas-dashboard/utils/auth_common.py 2>/dev/null || echo 'auth_common.pyが見つかりません'

echo ''
echo '6. 環境変数:'
env | grep -i 'NAS_MODE\|EXTERNAL'
"
```

### ステップ2: 起動ログを確認

```bash
cd ~/nas-project/meeting-minutes-byc
sudo docker compose logs meeting-minutes-byc | grep -i "認証\|auth" | head -20
```

### ステップ3: 実際のリクエストログを確認

```bash
cd ~/nas-project/meeting-minutes-byc
sudo docker compose logs -f meeting-minutes-byc
```

ブラウザで直接アクセスして、以下のようなログが表示されるか確認：
```
[AUTH] 認証が必要です: / -> http://192.168.68.110:9001/login
```

---

## 🔧 トラブルシューティング

### /nas-project が見つからない場合

`docker-compose.yml`にマウント設定を追加する必要があります：

```yaml
volumes:
  # 既存のマウント
  - /home/AdminUser/nas-project-data/meeting-minutes-byc/uploads:/app/uploads
  - /home/AdminUser/nas-project-data/meeting-minutes-byc/transcripts:/app/transcripts
  - /home/AdminUser/nas-project-data/meeting-minutes-byc/logs:/app/logs
  # 認証データベースのマウント（読み取り専用）
  - /home/AdminUser/nas-project-data:/nas-project-data:ro
  # nas-dashboardのutilsディレクトリへのアクセス（認証モジュール用）
  - /home/AdminUser/nas-project/nas-dashboard:/nas-project/nas-dashboard:ro
  # nas-project全体のマウント（必要に応じて）
  - /home/AdminUser/nas-project:/nas-project:ro
```

### app.pyが見つからない場合

コンテナ内の実際の作業ディレクトリを確認：

```bash
sudo docker compose exec meeting-minutes-byc pwd
sudo docker compose exec meeting-minutes-byc ls -la
```

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

