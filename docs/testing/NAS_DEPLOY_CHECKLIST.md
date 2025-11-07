# NAS環境へのデプロイチェックリスト

## 📋 概要

ローカル環境で行った変更をNAS環境にデプロイする手順です。

## 🚀 デプロイ手順

### 1. ローカル環境で変更を確認

```bash
cd /Users/Yoshi/nas-project

# 変更がコミットされているか確認
git log --oneline -5

# リモートにプッシュされているか確認
git status
```

### 2. NAS環境にSSH接続

```bash
ssh -p 23456 AdminUser@192.168.68.110
```

### 3. NAS環境で最新コードを取得

```bash
cd ~/nas-project

# 最新のコードを取得
git pull origin feature/monitoring-fail2ban-integration

# または、特定のブランチを取得
git fetch origin
git checkout feature/monitoring-fail2ban-integration
git pull origin feature/monitoring-fail2ban-integration
```

### 4. 各システムを再ビルド・再起動

#### nas-dashboard

```bash
cd ~/nas-project/nas-dashboard

# コンテナを再起動（変更を反映）
docker compose restart

# または、完全に再ビルドする場合
docker compose down
docker compose build --no-cache
docker compose up -d
```

#### document-automation

```bash
cd ~/nas-project/document-automation

# コンテナを再起動
docker compose restart web

# または、完全に再ビルドする場合
docker compose down
docker compose build --no-cache web
docker compose up -d
```

#### amazon-analytics

```bash
cd ~/nas-project/amazon-analytics

# コンテナを再起動
docker compose restart

# または、完全に再ビルドする場合
docker compose down
docker compose build --no-cache
docker compose up -d
```

#### youtube-to-notion

```bash
cd ~/nas-project/youtube-to-notion

# コンテナを再起動
docker compose restart

# または、完全に再ビルドする場合
docker compose down
docker compose build --no-cache
docker compose up -d
```

#### meeting-minutes-byc

```bash
cd ~/nas-project/meeting-minutes-byc

# コンテナを再起動
docker compose restart

# または、完全に再ビルドする場合
docker compose down
docker compose build --no-cache
docker compose up -d
```

#### notion-knowledge-summaries

```bash
cd ~/nas-project/notion-knowledge-summaries

# コンテナを再起動
docker compose restart

# または、完全に再ビルドする場合
docker compose down
docker compose build --no-cache
docker compose up -d
```

### 5. 確認

```bash
# 各コンテナの状態を確認
docker compose ps

# ログを確認（エラーがないか確認）
docker compose logs --tail=50
```

### 6. ブラウザで確認

- **ダッシュボード**: https://yoshi-nas-sys.duckdns.org:8443/
- **各システムの画面遷移を確認**

## 🔍 確認項目

### ダッシュボード

- [ ] ダッシュボードが表示される
- [ ] 各システムのボタンが表示される
- [ ] ボタンをクリックすると同じタブで開く（新規タブで開かない）

### 各システム画面

- [ ] ヘッダーが統一スタイルで表示される
- [ ] 戻るボタン（左矢印アイコン）が表示される
- [ ] 戻るボタンをクリックするとダッシュボードに戻る
- [ ] バージョン情報が右側に表示される
- [ ] タイトルがクリック可能でダッシュボードに戻る

### 画面遷移

- [ ] ダッシュボード → 各システム → ダッシュボードの遷移が正常に動作する
- [ ] ブラウザの戻るボタンでも正常に動作する

## ⚠️ 注意事項

1. **テンプレートファイルの変更**
   - テンプレートファイル（HTML）の変更は、コンテナを再起動するだけで反映されます
   - ただし、ボリュームマウントを使用している場合は、ファイルが直接反映されることがあります

2. **完全な再ビルドが必要な場合**
   - Dockerfileの変更があった場合
   - 依存関係（requirements.txtなど）の変更があった場合
   - 完全に再ビルドする必要があります

3. **キャッシュのクリア**
   - ブラウザのキャッシュをクリアして確認することを推奨します
   - または、シークレットモードで確認してください

## 🐛 トラブルシューティング

### 変更が反映されない

1. **コンテナが起動しているか確認**
   ```bash
   docker compose ps
   ```

2. **ログを確認**
   ```bash
   docker compose logs --tail=100
   ```

3. **ボリュームマウントを確認**
   ```bash
   docker compose config | grep volumes
   ```

4. **テンプレートファイルのパスを確認**
   ```bash
   docker exec <container_name> ls -la /app/templates/
   ```

### コンテナが起動しない

1. **ログを確認**
   ```bash
   docker compose logs
   ```

2. **イメージを再ビルド**
   ```bash
   docker compose down
   docker compose build --no-cache
   docker compose up -d
   ```

3. **ボリュームを削除して再作成**
   ```bash
   docker compose down -v
   docker compose up -d
   ```

---

**更新日**: 2025-11-06  
**作成者**: AI Assistant

