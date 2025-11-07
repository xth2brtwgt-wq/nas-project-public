# 統合管理ダッシュボード バージョン情報
# NAS Integrated Management Dashboard Version Information

__version__ = "1.7.1"
__version_info__ = (1, 7, 1)
__build_date__ = "2025-10-26"
__author__ = "Yoshi"
__description__ = "NAS統合管理ダッシュボード"

# バージョン履歴
VERSION_HISTORY = [
    {
        "version": "1.7.1",
        "date": "2025-11-07",
        "changes": [
            "fix: DB管理画面のテーブル表示不具合を修正"
        ]
    },
    {
        "version": "1.7.0",
        "date": "2025-11-07",
        "changes": [
            "feat: フロントエンドにブラックリストIP管理UIを追加"
        ]
    },
    {
        "version": "1.6.3",
        "date": "2025-11-07",
        "changes": [
            "fix: ESLintエラーを修正（confirmをwindow.confirmに変更）"
        ]
    },
    {
        "version": "1.6.2",
        "date": "2025-11-06",
        "changes": [
            "fix: Dockerログ取得処理の改善"
        ]
    },
    {
        "version": "1.6.1",
        "date": "2025-11-06",
        "changes": [
            "chore: nas-dashboardバージョンを1.6.0に更新"
        ]
    },
    {
        "version": "1.6.0",
        "date": "2025-11-06",
        "changes": [
            "feat: 管理者機能の制限とyoshi追加、.env.restoreバックアップ追加"
        ]
    },
    {
        "version": "1.5.0",
        "date": "2025-10-26",
        "changes": [
            "AI分析機能の統合実装",
            "セキュリティ分析とログ分析のAI化",
            "Dockerログ分析の生ログテキスト方式実装",
            "ハイブリッドログ分析機能（テキストログ + Dockerログ）",
            "システムタイプ自動判定機能",
            "月次AI分析レポート自動送信機能",
            "週次レポート・月次レポートのスケジューラー実装",
            "レポート管理機能の改善",
            "重複機能の削除と整理",
            "ログ監視機能の統合実装",
            "ログ監視専用画面(/logs)の追加",
            "全プロジェクトログとDockerコンテナログの統合表示",
            "ログレベル別フィルタリング機能（INFO、WARNING、ERROR、DEBUG）",
            "リアルタイム自動更新機能（30秒間隔）",
            "設定ファイルベースのログ管理機能",
            "メンテナンス性を重視した設定ファイル管理",
            "Insta360ログ確認セクションの削除（重複解消）",
            "レスポンシブデザイン対応のログ監視画面",
            "クイックリンクによるセクション間ナビゲーション"
        ]
    },
    {
        "version": "1.4.1",
        "date": "2025-10-20",
        "changes": [
                "自動バージョン管理システムを実装",
                "欠落していたupdateInsta360Logs関数を追加",
                "gunicornのタイムアウトを120秒に延長、アクセスログを有効化",
                "HTMLファイルの閉じタグを追加（</script>, </body>, </html>）",
                "v1.4.0: UPS監視機能の削除とBAN履歴表示件数の削減"
        ]
    },
    {
        "version": "1.4.0",
        "date": "2025-10-20",
        "changes": [
            "UPS監視機能の削除（ユーザーリクエストによる）",
            "BAN履歴の表示件数を50件から20件に削減",
            "UIの簡素化とパフォーマンス改善",
            "不要なAPIエンドポイントの削除"
        ]
    },
    {
        "version": "1.3.0",
        "date": "2025-10-20",
        "changes": [
            "UPS監視機能の統合実装（後に削除）",
            "NAS接続UPSのリアルタイム監視機能",
            "UPS状態表示（バッテリー残量・残り時間・電圧）",
            "UPS接続テスト機能の実装",
            "UPS監視ログ表示機能",
            "UPS設定変更機能",
            "接続テスト結果の表示時間延長機能",
            "自動更新の一時停止・再開機能",
            "UPS監視UIの3カラムレイアウト化",
            "新しいAPIエンドポイントの追加（/api/ups/status, /api/ups/test, /api/ups/logs, /api/ups/config）",
            "UPS監視スクリプトとの統合（ups_monitor_enhanced.sh）"
        ]
    },
    {
        "version": "1.2.0",
        "date": "2025-10-19",
        "changes": [
            "Fail2Ban監視機能の大幅強化",
            "リアルタイム監視機能の実装",
            "jail別詳細情報表示機能の追加",
            "BAN履歴表示機能の実装",
            "手動BAN解除機能の実装",
            "セキュリティ統計ダッシュボードの追加",
            "Fail2Ban監視UIの3カラムレイアウト化",
            "新しいAPIエンドポイントの追加（/api/fail2ban/jails, /api/fail2ban/ban-history, /api/fail2ban/unban）"
        ]
    },
    {
        "version": "1.1.0",
        "date": "2025-10-19",
        "changes": [
            "週次レポート機能の大幅改善",
            "実際のシステムデータに基づくレポート生成",
            "リアルタイムのCPU・メモリ・ディスク使用率取得",
            "実際のFail2Banデータの取得と表示",
            "Dockerコンテナの実際の状態取得",
            "動的な推奨事項の生成",
            "システム状況の自動評価（正常・注意・危険）",
            "詳細なレポート内容の改善"
        ]
    },
    {
        "version": "1.0.0",
        "date": "2025-10-19",
        "changes": [
            "初回リリース",
            "システム監視機能（CPU・メモリ・ディスク使用率）",
            "サービス管理機能（議事録生成・ドキュメント自動処理・Fail2Ban監視）",
            "セキュリティ監視機能（Fail2Ban状況確認）",
            "バックアップ管理機能（手動バックアップ作成・履歴確認）",
            "レポート機能（週次レポート手動生成）",
            "Dockerコンテナ管理機能",
            "レスポンシブデザイン対応"
        ]
    }
]

def get_version():
    """バージョン情報を取得"""
    return {
        "version": __version__,
        "version_info": __version_info__,
        "build_date": __build_date__,
        "author": __author__,
        "description": __description__,
        "history": VERSION_HISTORY
    }

def get_version_string():
    """バージョン文字列を取得"""
    return f"v{__version__}"

def get_full_version_info():
    """完全なバージョン情報を取得"""
    return f"{__description__} {get_version_string()} (Build: {__build_date__})"
