# Git & バージョン管理

## ブランチ戦略
- **main ブランチへの直接プッシュは推奨しない**
- 可能な限り feature ブランチから Pull Request 経由で行う（GitHub/GitLab等を使用している場合）
- main ブランチは常にデプロイ可能状態を維持
- ブランチ命名規則: `feature/機能名`、`fix/修正内容`、`docs/ドキュメント更新内容`
- 注: 個人プロジェクトや小規模な場合は、直接mainブランチへのコミットも許容

## コミットメッセージ
**Conventional Commits** 形式を厳密に適用：
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Type（必須）
- `feat`: 新機能の追加
- `fix`: バグ修正
- `docs`: ドキュメントの変更
- `style`: フォーマット、セミコロン追加など（機能に影響しない変更）
- `refactor`: リファクタリング（機能追加でもバグ修正でもない変更）
- `perf`: パフォーマンス改善
- `test`: テストの追加や修正
- `chore`: ビルドプロセス、補助ツール、ライブラリの変更

### 例
```
feat(auth): ユーザー認証機能を追加

Google OAuth 2.0を使用したログイン機能を実装
- OAuth認証フローの実装
- ユーザー情報の取得と保存
- セッション管理の追加

Closes #123
```

## Pull Request
- **PR作成を推奨**: 可能な限りPR経由で変更を行う（GitHub/GitLab等を使用している場合）
- **詳細なPR概要**: 以下の項目を含める
  ```markdown
  ## 概要
  この変更の目的と背景を説明

  ## 変更内容
  - 変更点1
  - 変更点2
  - 変更点3

  ## テスト
  - [ ] 単体テストを追加/更新
  - [ ] 手動テストを実施
  - [ ] 既存機能への影響確認

  ## 関連Issue
  Closes #[issue番号]

  ## スクリーンショット（UI変更の場合）
  変更前/変更後の画像

  ## レビューポイント
  特に注意してレビューしてほしい箇所
  ```

## コミット粒度
- **論理的な単位**でコミットを分割
- 1つのコミットは1つの責務のみ
- 「とりあえず」や「WIP」コミットは避ける
- コミット前に `git diff` で変更内容を確認

## コミット前の確認事項

### バージョンファイルの確認

自動バージョンアップシステムにより、コミット時にバージョンファイルが自動的に更新されますが、**コミットに含まれているか必ず確認してください**：

```bash
# コミット前にステージングされているファイルを確認
git status

# バージョンファイルが含まれているか確認
git diff --cached config/version.py
# または
git diff --cached meeting-minutes-byc/config/version.py
```

### バージョンファイルがコミットされていない場合

もしバージョンファイルがコミットされていない場合、以下の問題が発生する可能性があります：

1. **NAS環境に古いバージョンが残る**
   - ローカルには新しいバージョン（例：1.7.3）があるが、リモートには古いバージョン（例：1.6.0）が残る
   - NAS環境で`git pull`しても古いバージョンが取得される

2. **次回の修正時の問題**
   - ローカルのバージョン（1.7.3）からさらにインクリメントされる（1.7.4）
   - リモートのバージョン（1.6.0）との不整合が発生する可能性がある

### 対処法

バージョンファイルがコミットされていない場合：

```bash
# 1. 未コミットのバージョンファイルを確認
git status meeting-minutes-byc/config/version.py

# 2. バージョンファイルを明示的にコミット
git add meeting-minutes-byc/config/version.py
git commit -m "chore: バージョンを1.7.3に更新"
git push origin main

# 3. NAS環境で最新を取得
ssh -p 23456 AdminUser@192.168.68.110 "cd ~/nas-project/meeting-minutes-byc && git pull origin main"
```

### コミット後の確認

コミット後、バージョンファイルが含まれているか確認：

```bash
# 最新のコミットにバージョンファイルが含まれているか確認
git show HEAD --name-only | grep version
```

## バージョン管理
- バージョン情報はconfig/version.pyで一元管理
- セマンティックバージョニング（major.minor.patch）を採用
- 変更時はVERSION_HISTORYに追加
- タグを使用してリリースポイントを明示
- リリースノートで変更内容を明確に記載
- 全プロジェクトで統一されたバージョン管理

詳細は [VERSION_MANAGEMENT.md](../../VERSION_MANAGEMENT.md) を参照してください。

