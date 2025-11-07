# 📋 共通認証モジュール 実装計画

**作成日**: 2025-11-04  
**目的**: 各サービスで共有する認証モジュールの設計

---

## 🎯 目標

各サービス（`meeting-minutes-byc`、`amazon-analytics`、`document-automation`、`youtube-to-notion`、`nas-dashboard-monitoring`）でダッシュボードと同じ認証システムを使用できるようにする。

---

## 📊 現在の状況

### ダッシュボード側
- ✅ 認証データベース: `nas-dashboard/utils/auth_db.py`
- ✅ セッション管理: CookieベースのセッションID
- ✅ データベースパス: `/nas-project-data/nas-dashboard/auth.db`

### 各サービス
- ❌ 認証機能なし（直接アクセス可能）

---

## 🔧 実装方針

### 1. 共通認証モジュールの作成

**場所**: `nas-dashboard/utils/auth_common.py`

**機能**:
- セッション検証関数
- ユーザー情報取得関数
- フレームワーク非依存の認証ロジック

### 2. 各サービスへの統合

**Flask用** (`meeting-minutes-byc`, `youtube-to-notion`):
- デコレータ `@require_auth`
- `get_current_user()` 関数

**FastAPI用** (`amazon-analytics`, `document-automation`, `nas-dashboard-monitoring`):
- 依存性注入 `Depends(get_current_user)`
- ミドルウェア関数

### 3. データベース共有

すべてのサービスで同じデータベースファイルを使用：
- パス: `/nas-project-data/nas-dashboard/auth.db` (コンテナ内)
- マウント: `/home/AdminUser/nas-project-data:/nas-project-data:rw` (docker-compose.yml)

---

## 📝 実装手順

### ステップ1: 共通認証モジュールの作成
- [ ] `nas-dashboard/utils/auth_common.py` を作成
- [ ] セッション検証関数を実装
- [ ] ユーザー情報取得関数を実装

### ステップ2: Flask用ミドルウェアの作成
- [ ] `meeting-minutes-byc` に統合
- [ ] `youtube-to-notion` に統合

### ステップ3: FastAPI用ミドルウェアの作成
- [ ] `amazon-analytics` に統合
- [ ] `document-automation` に統合
- [ ] `nas-dashboard-monitoring` に統合

### ステップ4: 動作確認
- [ ] 各サービスで認証が動作することを確認
- [ ] 未認証時のリダイレクト動作を確認

---

## 🔍 技術的な考慮事項

### Cookieの共有
- ドメイン: `yoshi-nas-sys.duckdns.org`
- パス: `/`
- SameSite: `None` (クロスサイト対応)
- Secure: `True` (HTTPS必須)

### セッション検証
- セッションIDをCookieから取得
- データベースでセッションを検証
- 有効期限をチェック

### エラーハンドリング
- 未認証時: ダッシュボードのログインページにリダイレクト
- セッション期限切れ: ログインページにリダイレクト
- データベースエラー: ログに記録し、エラーレスポンスを返す

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

