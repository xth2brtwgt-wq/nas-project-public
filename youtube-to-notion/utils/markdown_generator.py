#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown生成ユーティリティ
YouTube動画要約のMarkdownファイル生成
meeting-minutes-bycの機能を流用・拡張
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MarkdownGenerator:
    def __init__(self):
        pass
    
    def save_youtube_summary(self, video_info, summary, transcript, output_dir):
        """YouTube動画要約をMarkdownファイルとして保存"""
        try:
            # ファイル名を生成
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            video_id = video_info.get('video_id', 'unknown')
            safe_title = self._sanitize_filename(video_info.get('title', 'YouTube動画'))
            filename = f"youtube_summary_{timestamp}_{video_id}.md"
            filepath = os.path.join(output_dir, filename)
            
            # Markdownコンテンツを生成
            markdown_content = self._generate_markdown_content(video_info, summary, transcript)
            
            # ファイルに保存
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Markdownファイル保存完了: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Markdown生成エラー: {str(e)}")
            raise Exception(f"Markdown生成に失敗しました: {str(e)}")
    
    def _generate_markdown_content(self, video_info, summary, transcript):
        """Markdownコンテンツを生成"""
        content = []
        
        # ヘッダー
        content.append(f"# {video_info.get('title', 'YouTube動画要約')}")
        content.append("")
        content.append(f"**生成日時:** {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        content.append("")
        
        # 動画情報セクション
        content.append("## 📺 動画情報")
        content.append("")
        content.append(f"- **タイトル:** {video_info.get('title', '')}")
        content.append(f"- **チャンネル:** {video_info.get('channel', '')}")
        content.append(f"- **再生時間:** {video_info.get('duration_formatted', '')}")
        content.append(f"- **アップロード日:** {video_info.get('upload_date', '')}")
        content.append(f"- **視聴回数:** {video_info.get('view_count', 0):,}回")
        content.append(f"- **いいね数:** {video_info.get('like_count', 0):,}回")
        content.append(f"- **カテゴリ:** {video_info.get('category', '')}")
        content.append(f"- **言語:** {video_info.get('language', '')}")
        content.append(f"- **URL:** {video_info.get('url', '')}")
        content.append("")
        
        # サムネイル画像
        if video_info.get('thumbnail'):
            content.append(f"![サムネイル]({video_info.get('thumbnail')})")
            content.append("")
        
        # 要約セクション
        content.append("## 📝 要約")
        content.append("")
        content.append(summary)
        content.append("")
        
        # 文字起こしセクション
        content.append("## 📄 文字起こし全文")
        content.append("")
        content.append("<details>")
        content.append("<summary>文字起こしを表示/非表示</summary>")
        content.append("")
        content.append(transcript)
        content.append("")
        content.append("</details>")
        content.append("")
        
        # メタデータ
        content.append("---")
        content.append("")
        content.append("## 📊 メタデータ")
        content.append("")
        content.append(f"- **処理日時:** {datetime.now().isoformat()}")
        content.append(f"- **動画ID:** {video_info.get('video_id', '')}")
        content.append(f"- **文字数:** {len(transcript):,}文字")
        content.append(f"- **要約長:** {len(summary):,}文字")
        content.append("")
        
        return "\n".join(content)
    
    def _sanitize_filename(self, filename):
        """ファイル名に使用できない文字を除去"""
        import re
        # ファイル名に使用できない文字を除去
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
        # 長すぎる場合は切り詰め
        if len(sanitized) > 50:
            sanitized = sanitized[:50]
        return sanitized
    
    def generate_youtube_markdown(self, video_info, summary, transcript, keywords=None, category=None, date=None, include_timestamps=False):
        """YouTube動画要約のMarkdownコンテンツを生成"""
        try:
            content = []
            
            # ヘッダー
            content.append(f"# {video_info.get('title', 'YouTube動画要約')}")
            content.append("")
            content.append(f"**生成日時:** {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
            content.append("")
            
            # 動画情報セクション
            content.append("## 📺 動画情報")
            content.append("")
            content.append(f"- **タイトル:** {video_info.get('title', '')}")
            content.append(f"- **チャンネル:** {video_info.get('channel', '')}")
            content.append(f"- **再生時間:** {video_info.get('duration_formatted', '')}")
            content.append(f"- **アップロード日:** {video_info.get('upload_date', '')}")
            content.append(f"- **視聴回数:** {video_info.get('view_count', 0):,}回")
            content.append(f"- **URL:** {video_info.get('url', '')}")
            content.append("")
            
            # 要約セクション
            content.append("## 📝 要約")
            content.append("")
            content.append(summary)
            content.append("")
            
            # キーワードセクション
            if keywords:
                content.append("## 🏷️ キーワード")
                content.append("")
                if isinstance(keywords, list):
                    for keyword in keywords:
                        content.append(f"- {keyword}")
                else:
                    content.append(f"- {keywords}")
                content.append("")
            
            # カテゴリセクション
            if category:
                content.append("## 📂 カテゴリ")
                content.append("")
                content.append(f"- {category}")
                content.append("")
            
            # 文字起こしセクション
            content.append("## 📄 文字起こし全文")
            content.append("")
            content.append("<details>")
            content.append("<summary>文字起こしを表示/非表示</summary>")
            content.append("")
            content.append(transcript)
            content.append("")
            content.append("</details>")
            content.append("")
            
            return "\n".join(content)
            
        except Exception as e:
            logger.error(f"Markdown生成エラー: {str(e)}")
            raise Exception(f"Markdown生成に失敗しました: {str(e)}")

    def generate_summary_report(self, summaries, output_dir):
        """複数の要約をまとめたレポートを生成"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"youtube_summary_report_{timestamp}.md"
            filepath = os.path.join(output_dir, filename)
            
            content = []
            content.append("# YouTube要約レポート")
            content.append("")
            content.append(f"**生成日時:** {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
            content.append(f"**要約数:** {len(summaries)}件")
            content.append("")
            
            # カテゴリ別集計
            categories = {}
            for summary in summaries:
                category = summary.get('video_info', {}).get('category', 'その他')
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1
            
            content.append("## 📊 カテゴリ別集計")
            content.append("")
            for category, count in categories.items():
                content.append(f"- **{category}:** {count}件")
            content.append("")
            
            # 各要約の詳細
            for i, summary in enumerate(summaries, 1):
                video_info = summary.get('video_info', {})
                content.append(f"## {i}. {video_info.get('title', '')}")
                content.append("")
                content.append(f"- **チャンネル:** {video_info.get('channel', '')}")
                content.append(f"- **カテゴリ:** {video_info.get('category', '')}")
                content.append(f"- **URL:** {video_info.get('url', '')}")
                content.append("")
                content.append("### 要約")
                content.append("")
                content.append(summary.get('summary', ''))
                content.append("")
                content.append("---")
                content.append("")
            
            # ファイルに保存
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
            
            logger.info(f"要約レポート生成完了: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"要約レポート生成エラー: {str(e)}")
            raise Exception(f"要約レポート生成に失敗しました: {str(e)}")
