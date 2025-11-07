# 管理者機能ボタン表示制御 - デプロイ手順

## 問題
権限がないユーザーでも管理機能ボタンが表示されている

## 原因
Dockerイメージにコードが組み込まれているため、`docker compose restart`だけでは最新コードが反映されない

## 解決方法
イメージを再ビルドして最新コードを反映する

## デプロイ手順

### 1. 最新コードを取得
```bash
cd ~/nas-project
git pull origin feature/monitoring-fail2ban-integration
```

### 2. イメージを再ビルドしてコンテナを再起動
```bash
cd nas-dashboard
docker compose build --no-cache
docker compose up -d
```

または、一括で実行：
```bash
cd ~/nas-project/nas-dashboard
docker compose build --no-cache && docker compose up -d
```

### 3. ログ確認
```bash
docker logs nas-dashboard --tail 50 | grep -E "\[DASHBOARD\]|\[ADMIN\]"
```

以下のログが表示されることを確認：
- `[DASHBOARD] 管理者判定を開始: user=...`
- `[ADMIN] DASHBOARD_ADMIN_USERS環境変数: '...'`
- `[ADMIN] ユーザー '...' (ID: ...) の管理者チェック: ...`
- `[DASHBOARD] 管理者判定結果: is_admin=...`

## 動作確認

### 管理者ユーザー（ID=1、またはDASHBOARD_ADMIN_USERSで指定）
- すべての管理機能ボタンが表示される

### 一般ユーザー
- 管理機能ボタンが非表示になる
