# 🔒 Fail2banコンテナの確認ガイド

**作成日**: 2025-11-02  
**対象**: Dockerコンテナとして動作しているFail2ban

---

## 📋 現在の状況

nas-dashboard-monitoringのコードを確認したところ、**Fail2banはDockerコンテナ（`fail2ban`）として動作している**ことがわかりました。

---

## 🔍 確認手順

### ステップ1: Fail2banコンテナの状態確認

NAS上で以下を実行してください：

```bash
# Fail2banコンテナが存在するか確認
docker ps -a | grep fail2ban

# コンテナが起動しているか確認
docker ps | grep fail2ban

# コンテナの詳細情報を確認
docker inspect fail2ban 2>/dev/null || echo "コンテナが見つかりません"
```

---

### ステップ2: Fail2banコンテナの状態確認（コンテナ内）

コンテナが起動している場合：

```bash
# Fail2banの状態を確認（コンテナ経由）
docker exec fail2ban fail2ban-client status

# 有効なjailの一覧を確認
docker exec fail2ban fail2ban-client status | grep "Jail list"

# SSH jailの状態を確認
docker exec fail2ban fail2ban-client status sshd
```

---

### ステップ3: nas-dashboard-monitoringでの確認

監視システムからFail2banの状態を確認します：

```bash
# nas-dashboard-monitoringの環境変数を確認
docker exec nas-dashboard-monitoring-backend env | grep NAS_MODE

# APIエンドポイントでFail2ban状態を確認
curl http://192.168.68.110:8002/api/v1/security/fail2ban/status
```

---

### ステップ4: Fail2banコンテナのログ確認

```bash
# Fail2banコンテナのログを確認
docker logs fail2ban --tail 50

# エラーがないか確認
docker logs fail2ban 2>&1 | grep -i error | tail -20
```

---

## 🛠️ もしFail2banコンテナが存在しない、または起動していない場合

### ステップ1: コンテナの有無を確認

```bash
# 全てのコンテナを確認
docker ps -a

# fail2banという名前のコンテナを確認
docker ps -a | grep -i fail2ban
```

### ステップ2: Fail2banコンテナの設定ファイルを確認

プロジェクト内のFail2ban設定を確認：

```bash
# 設定ファイルの場所を確認
ls -la docker/fail2ban/

# docker-compose.ymlまたはDockerfileがあるか確認
find . -name "*fail2ban*" -type f
```

---

## ✅ 確認すべき項目

- [ ] Fail2banコンテナが存在する
- [ ] Fail2banコンテナが起動している
- [ ] Fail2banコンテナ内でFail2banサービスが稼働している
- [ ] nas-dashboard-monitoringの環境変数`NAS_MODE`が設定されている
- [ ] 監視システムからFail2ban状態を取得できる

---

## 🔍 次のステップ

1. **コンテナが存在して起動している場合**
   - コンテナ内の設定を確認（SSHポート23456が監視されているか）
   - nas-dashboard-monitoringから状態を確認

2. **コンテナが存在しない、または起動していない場合**
   - Fail2banコンテナの設定ファイルを確認
   - 必要に応じてコンテナを起動または作成

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

