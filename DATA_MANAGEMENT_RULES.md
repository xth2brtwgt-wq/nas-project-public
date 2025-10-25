# データ管理ルール

## 📋 概要

NAS環境でのデータ管理に関する統一ルールです。
全プロジェクトで一貫したデータ管理を実現し、効率的なバックアップとメンテナンスを可能にします。

## 🏗️ データディレクトリ構造

### 統合データディレクトリ

```
/home/YOUR_USERNAME/nas-project-data/     # 統合データディレクトリ（全データを一元管理）
├── amazon-analytics/                 # Amazon購入分析データ
│   ├── cache/                        # キャッシュデータ
│   ├── db/                          # データベース
│   ├── exports/                     # エクスポートファイル
│   ├── processed/                   # 処理済みデータ
│   └── uploads/                     # アップロードファイル
├── document-automation/              # ドキュメント自動化データ
│   ├── cache/                       # キャッシュデータ
│   ├── db/                          # データベース
│   ├── exports/                     # エクスポートファイル
│   ├── processed/                   # 処理済みデータ
│   ├── qdrant/                      # ベクトルデータベース
│   └── uploads/                     # アップロードファイル
├── meeting-minutes-byc/              # 議事録データ
│   ├── logs/                        # ログファイル
│   ├── transcripts/                 # 音声転写データ
│   └── uploads/                     # アップロードファイル
├── nas-dashboard/                    # ダッシュボードデータ
│   ├── backups/                     # バックアップファイル
│   └── reports/                     # レポートファイル
└── youtube-to-notion/                # YouTube to Notionデータ
    ├── cache/                       # キャッシュデータ
    ├── logs/                        # ログファイル
    ├── outputs/                     # 出力ファイル
    └── uploads/                     # アップロードファイル
```

## 📝 データ保存ルール

### 1. 基本原則

#### **データ分離の徹底**
- **ソースコード**: `/home/YOUR_USERNAME/nas-project/`（Git管理）
- **データ**: `/home/YOUR_USERNAME/nas-project-data/`（統合管理）
- **禁止**: ソースコードディレクトリ内にデータを保存しない

#### **統合データディレクトリの使用**
- **必須**: 全プロジェクトのデータは `/home/YOUR_USERNAME/nas-project-data/` 配下に保存
- **禁止**: `/home/YOUR_USERNAME/{プロジェクト名}-data/` 形式での個別ディレクトリ作成
- **命名規則**: プロジェクト名は小文字、ハイフン区切り（例: `new-project-name`）

### 2. ディレクトリ作成ルール

#### **新規プロジェクトデータディレクトリの作成**

```bash
# 統合データディレクトリ配下にプロジェクトデータディレクトリを作成
mkdir -p /home/YOUR_USERNAME/nas-project-data/{プロジェクト名}/

# 標準的なサブディレクトリの作成
mkdir -p /home/YOUR_USERNAME/nas-project-data/{プロジェクト名}/uploads
mkdir -p /home/YOUR_USERNAME/nas-project-data/{プロジェクト名}/logs
mkdir -p /home/YOUR_USERNAME/nas-project-data/{プロジェクト名}/cache
mkdir -p /home/YOUR_USERNAME/nas-project-data/{プロジェクト名}/processed
mkdir -p /home/YOUR_USERNAME/nas-project-data/{プロジェクト名}/exports

# 権限設定
chmod 755 /home/YOUR_USERNAME/nas-project-data/{プロジェクト名}
chmod 755 /home/YOUR_USERNAME/nas-project-data/{プロジェクト名}/*

# 所有者設定
chown -R YOUR_USERNAME:admin /home/YOUR_USERNAME/nas-project-data/{プロジェクト名}
```

#### **Docker Compose設定**

```yaml
volumes:
  # 統合データディレクトリを使用
  - /home/YOUR_USERNAME/nas-project-data/{プロジェクト名}/uploads:/app/uploads
  - /home/YOUR_USERNAME/nas-project-data/{プロジェクト名}/logs:/app/logs
  - /home/YOUR_USERNAME/nas-project-data/{プロジェクト名}/cache:/app/cache
  - /home/YOUR_USERNAME/nas-project-data/{プロジェクト名}/processed:/app/processed
  - /home/YOUR_USERNAME/nas-project-data/{プロジェクト名}/exports:/app/exports
```

### 3. データタイプ別ルール

#### **アップロードファイル（uploads/）**
- **用途**: ユーザーがアップロードしたファイル
- **保持期間**: プロジェクト固有のルールに従う
- **クリーンアップ**: 定期的な古いファイルの削除を推奨

#### **ログファイル（logs/）**
- **用途**: アプリケーションログ、エラーログ
- **保持期間**: 30日間（設定可能）
- **ローテーション**: 自動ローテーションを推奨

#### **キャッシュデータ（cache/）**
- **用途**: 一時的なキャッシュデータ
- **保持期間**: 7日間
- **クリーンアップ**: 定期的な削除を推奨

#### **処理済みデータ（processed/）**
- **用途**: 処理済みのデータファイル
- **保持期間**: プロジェクト固有のルールに従う
- **バックアップ**: 重要なデータはバックアップ対象

#### **エクスポートファイル（exports/）**
- **用途**: エクスポートされたレポート、データ
- **保持期間**: 90日間
- **アーカイブ**: 古いファイルはアーカイブ化

### 4. バックアップルール

#### **統合データディレクトリのバックアップ**

```bash
# 統合データディレクトリの一括バックアップ
tar -czf /home/YOUR_USERNAME/backups/nas-project-data-$(date +%Y%m%d_%H%M%S).tar.gz \
    /home/YOUR_USERNAME/nas-project-data/

# プロジェクト別バックアップ
for project in amazon-analytics document-automation meeting-minutes-byc nas-dashboard youtube-to-notion; do
    tar -czf /home/YOUR_USERNAME/backups/${project}-$(date +%Y%m%d_%H%M%S).tar.gz \
        /home/YOUR_USERNAME/nas-project-data/${project}/
done
```

#### **バックアップスケジュール**
- **日次**: 重要なデータの増分バックアップ
- **週次**: 全データの完全バックアップ
- **月次**: 長期保存用アーカイブ

### 5. クリーンアップルール

#### **自動クリーンアップの実装**

```bash
# 古いファイルの削除（30日以上前）
find /home/YOUR_USERNAME/nas-project-data/ -type f -mtime +30 -delete

# 空ディレクトリの削除
find /home/YOUR_USERNAME/nas-project-data/ -type d -empty -delete

# ログファイルのローテーション
find /home/YOUR_USERNAME/nas-project-data/ -name "*.log" -mtime +7 -delete
```

#### **プロジェクト固有のクリーンアップ**

```bash
# YouTube音声ファイルのクリーンアップ（1週間後削除）
find /home/YOUR_USERNAME/nas-project-data/youtube-to-notion/uploads/ \
    -name "*.mp3" -o -name "*.webm" -mtime +7 -delete

# 議事録ファイルのクリーンアップ（90日後削除）
find /home/YOUR_USERNAME/nas-project-data/meeting-minutes-byc/transcripts/ \
    -name "*.txt" -o -name "*.json" -mtime +90 -delete
```

### 6. セキュリティルール

#### **権限設定**
- **所有者**: `YOUR_USERNAME:admin`
- **権限**: `755`（ディレクトリ）、`644`（ファイル）
- **機密ファイル**: `600`（APIキー、パスワード）

#### **アクセス制御**
- **データディレクトリ**: YOUR_USERNAMEのみアクセス可能
- **バックアップ**: 暗号化して保存
- **ログ**: 機密情報を含まないよう注意

### 7. 監視・アラートルール

#### **ディスク使用量監視**
```bash
# 統合データディレクトリの使用量監視
du -sh /home/YOUR_USERNAME/nas-project-data/

# プロジェクト別使用量監視
for project in amazon-analytics document-automation meeting-minutes-byc nas-dashboard youtube-to-notion; do
    echo "$project: $(du -sh /home/YOUR_USERNAME/nas-project-data/$project/ | cut -f1)"
done
```

#### **アラート条件**
- **ディスク使用量**: 80%以上で警告
- **ファイル数**: 10,000ファイル以上で警告
- **古いファイル**: 90日以上前のファイルが存在する場合

### 8. 移行ルール

#### **既存データの移行**
```bash
# 古いデータディレクトリから統合データディレクトリへ移行
mv /home/YOUR_USERNAME/{プロジェクト名}-data/ /home/YOUR_USERNAME/nas-project-data/{プロジェクト名}/

# 権限設定
chown -R YOUR_USERNAME:admin /home/YOUR_USERNAME/nas-project-data/{プロジェクト名}
chmod -R 755 /home/YOUR_USERNAME/nas-project-data/{プロジェクト名}
```

#### **Docker Compose設定の更新**
- **旧設定**: `/home/YOUR_USERNAME/{プロジェクト名}-data/`
- **新設定**: `/home/YOUR_USERNAME/nas-project-data/{プロジェクト名}/`

## 🎯 推奨事項

### 1. 定期的なメンテナンス
- **週次**: ディスク使用量の確認
- **月次**: 古いファイルのクリーンアップ
- **四半期**: バックアップの検証

### 2. 監視の設定
- **ディスク使用量**: 80%で警告、90%で緊急
- **ファイル数**: 異常な増加の監視
- **アクセス**: 不正アクセスの監視

### 3. ドキュメント化
- **データマップ**: 各プロジェクトのデータ構造を文書化
- **バックアップ手順**: 復旧手順を文書化
- **クリーンアップ手順**: 定期メンテナンス手順を文書化

## 📋 チェックリスト

### 新規プロジェクト作成時
- [ ] 統合データディレクトリ配下にプロジェクトディレクトリを作成
- [ ] 適切な権限設定（YOUR_USERNAME:admin, 755）
- [ ] Docker Compose設定で統合データディレクトリを使用
- [ ] クリーンアップルールの設定

### 既存プロジェクト移行時
- [ ] 古いデータディレクトリから統合データディレクトリへ移行
- [ ] Docker Compose設定の更新
- [ ] 権限設定の確認
- [ ] 動作確認

### 定期メンテナンス時
- [ ] ディスク使用量の確認
- [ ] 古いファイルのクリーンアップ
- [ ] バックアップの実行
- [ ] ログの確認

---

**作成日**: 2025年10月24日
**対象**: 全NAS環境プロジェクト
**更新**: 必要に応じて更新
