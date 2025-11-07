# 🔄 ダッシュボードタイトル更新手順

**作成日**: 2025-11-04  
**目的**: タイトル変更の反映

---

## 🔄 再起動手順

### ステップ1: 最新コードを取得

```bash
cd ~/nas-project/nas-dashboard
git pull origin feature/monitoring-fail2ban-integration
```

### ステップ2: コンテナを再起動

```bash
sudo docker compose restart nas-dashboard
```

### ステップ3: ブラウザのキャッシュをクリア

ブラウザで以下を実行：

1. **Safariの場合**:
   - `Cmd + Option + E` (キャッシュをクリア)
   - または、履歴をクリア > キャッシュをクリア

2. **Chrome/Edgeの場合**:
   - `Cmd + Shift + Delete` (履歴をクリア)
   - 「キャッシュされた画像とファイル」を選択

3. **強制リロード**:
   - `Cmd + Shift + R` (強制リロード)

### ステップ4: 確認

ブラウザで以下を確認：

- ログインページ: タイトルが「NAS-System」になっているか
- ダッシュボード: ナビゲーションバーのタイトルが「NAS-System」になっているか
- ブラウザのタブ: タイトルが「NAS-System」になっているか

---

## 🔍 トラブルシューティング

### タイトルが変わらない場合

1. **完全な再起動**:
   ```bash
   cd ~/nas-project/nas-dashboard
   sudo docker compose down
   sudo docker compose up -d
   ```

2. **ブラウザを完全に閉じて再起動**

3. **シークレットモード/プライベートモードで確認**

4. **開発者ツールで確認**:
   - `Cmd + Option + I` (開発者ツールを開く)
   - Networkタブで「Disable cache」をチェック
   - ページをリロード

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

