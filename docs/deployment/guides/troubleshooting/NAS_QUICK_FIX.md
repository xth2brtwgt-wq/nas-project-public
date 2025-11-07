# NASデプロイ - パーミッション問題の解決

## 🔧 パーミッションエラーの解決方法

### オプション1: ホームディレクトリを使用（推奨）

```bash
# ホームディレクトリに移動
cd ~

# プロジェクトをクローン
git clone git@github.com:xth2brtwgt-wq/dpx2800-nas-system.git nas-project
cd nas-project
```

### オプション2: sudo を使用

```bash
cd /volume1/docker
sudo git clone git@github.com:xth2brtwgt-wq/dpx2800-nas-system.git nas-project
sudo chown -R AdminUser:users nas-project
cd nas-project
```

### オプション3: 別のディレクトリを使用

```bash
# volume1 内の別の場所
cd /volume1/homes/AdminUser
git clone git@github.com:xth2brtwgt-wq/dpx2800-nas-system.git nas-project
cd nas-project
```

---

## ✅ 推奨: ホームディレクトリを使用

最もシンプルで安全な方法です：

```bash
AdminUser@DXP2800:/volume1/docker$ cd ~
AdminUser@DXP2800:~$ pwd
/var/services/homes/AdminUser

AdminUser@DXP2800:~$ git clone git@github.com:xth2brtwgt-wq/dpx2800-nas-system.git nas-project
AdminUser@DXP2800:~$ cd nas-project
AdminUser@DXP2800:~/nas-project$
```

以降の手順はすべて `~/nas-project` で実行します。

