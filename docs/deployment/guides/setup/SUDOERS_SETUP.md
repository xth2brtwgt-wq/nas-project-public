# 🔐 sudoers設定ガイド（証明書自動更新用）

**作成日**: 2025-11-02  
**対象**: 証明書自動更新スクリプトのcronジョブ実行

---

## 📋 概要

証明書自動更新スクリプトをcronジョブで実行する場合、`sudo`パスワードが必要なコマンドが含まれています。  
パスワードなしで実行できるように、`sudoers`ファイルを設定します。

---

## ⚠️ 注意事項

`sudoers`ファイルの設定を誤ると、システムにアクセスできなくなる可能性があります。  
**必ずバックアップを取ってから編集してください。**

---

## 🚀 設定手順

### ステップ1: sudoersファイルのバックアップ

```bash
# NASにSSH接続
ssh -p 23456 AdminUser@192.168.68.110

# sudoersファイルのバックアップ
sudo cp /etc/sudoers /etc/sudoers.backup

# バックアップの確認
ls -la /etc/sudoers*
```

### ステップ2: sudoersファイルを編集

```bash
# sudoersファイルを編集（visudoを使用 - 推奨）
sudo visudo

# または
sudo nano /etc/sudoers
```

### ステップ3: 証明書更新スクリプト用の設定を追加

ファイルの末尾に以下の行を追加：

```
# 証明書自動更新スクリプト用（パスワードなしで実行可能）
AdminUser ALL=(ALL) NOPASSWD: /bin/mkdir -p /etc/letsencrypt/live/*
AdminUser ALL=(ALL) NOPASSWD: /bin/cp /home/AdminUser/.acme.sh/yoshi-nas-sys.duckdns.org_ecc/* /etc/letsencrypt/live/yoshi-nas-sys.duckdns.org/*
AdminUser ALL=(ALL) NOPASSWD: /bin/chown root:root /etc/letsencrypt/live/yoshi-nas-sys.duckdns.org/*
AdminUser ALL=(ALL) NOPASSWD: /bin/chmod * /etc/letsencrypt/live/yoshi-nas-sys.duckdns.org/*
```

**注意**: パスを正しく指定してください。

### ステップ4: 設定の保存と確認

```bash
# 保存してエディタを終了（nanoの場合: Ctrl+X → Y → Enter）

# 設定の確認（構文チェック）
sudo visudo -c
```

**エラーが表示された場合**: すぐにバックアップから復元してください：

```bash
sudo cp /etc/sudoers.backup /etc/sudoers
```

### ステップ5: テスト

```bash
# パスワードなしでsudoが実行できるかテスト
sudo mkdir -p /etc/letsencrypt/live/test
sudo rm -rf /etc/letsencrypt/live/test

# パスワードが要求されなければ成功
```

---

## 🔄 別の方法: より柔軟な設定（推奨）

証明書更新スクリプト全体をパスワードなしで実行できるように設定：

```
# 証明書自動更新スクリプト用（パスワードなしで実行可能）
AdminUser ALL=(ALL) NOPASSWD: /home/AdminUser/bin/renew-cert-and-reload.sh
```

この方法の方が簡単で安全です。

---

## ⚠️ トラブルシューティング

### sudoersファイルを編集した後、ログインできなくなった場合

1. **物理的にNASにアクセスできる場合**:
   - コンソールから直接ログイン
   - バックアップから復元: `sudo cp /etc/sudoers.backup /etc/sudoers`

2. **リモートアクセスのみ可能な場合**:
   - 別のSSHセッションを開いて復元を試みる
   - または、NASのリセット（最終手段）

### 設定が反映されない場合

```bash
# sudoキャッシュをクリア
sudo -k

# 再度テスト
sudo mkdir -p /etc/letsencrypt/live/test
```

---

## 📝 チェックリスト

- [ ] sudoersファイルのバックアップを取得
- [ ] sudoersファイルを編集
- [ ] 設定を保存
- [ ] 構文チェック（`sudo visudo -c`）
- [ ] パスワードなしでsudoが実行できるかテスト
- [ ] cronジョブを設定
- [ ] cronジョブの動作確認

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

