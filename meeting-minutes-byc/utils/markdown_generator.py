#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown生成機能
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# アプリケーション情報
from config.version import APP_NAME, APP_VERSION

class MarkdownGenerator:
    def __init__(self):
        self.transcript_dir = os.getenv('TRANSCRIPT_DIR', './transcripts')
    
    def generate_meeting_markdown(self, meeting_data, output_dir=None):
        """議事録のMarkdownファイルを生成"""
        try:
            if not output_dir:
                output_dir = self.transcript_dir
            
            # ファイル名の生成
            meeting_date = meeting_data.get('meeting_date', datetime.now().strftime('%Y-%m-%d'))
            filename = meeting_data.get('filename', 'meeting')
            safe_filename = self._sanitize_filename(filename)
            
            md_filename = f"meeting_minutes_{meeting_date}_{safe_filename}.md"
            md_filepath = os.path.join(output_dir, md_filename)
            
            # Markdownコンテンツの生成
            content = self._create_markdown_content(meeting_data)
            
            # ファイルの書き込み
            with open(md_filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Markdownファイル生成完了: {md_filepath}")
            return md_filepath
            
        except Exception as e:
            logger.error(f"Markdownファイル生成エラー: {str(e)}")
            raise Exception(f"Markdownファイル生成に失敗しました: {str(e)}")
    
    def generate_transcript_file(self, meeting_data, output_dir=None):
        """文字起こしファイルを生成"""
        try:
            if not output_dir:
                output_dir = self.transcript_dir
            
            # ファイル名の生成（拡張子を除去）
            filename = meeting_data.get('filename', 'meeting')
            filename_without_ext = os.path.splitext(filename)[0]  # 拡張子を除去
            safe_filename = self._sanitize_filename(filename_without_ext)
            
            txt_filename = f"transcript_{safe_filename}.txt"
            txt_filepath = os.path.join(output_dir, txt_filename)
            
            # 文字起こしコンテンツの生成
            formatted_meeting_date = self._format_datetime(meeting_data.get('meeting_date', '未設定'))
            content = f"""文字起こし結果

ファイル名: {meeting_data.get('filename', '不明')}
会議日時: {formatted_meeting_date}
処理日時: {meeting_data.get('timestamp', '不明')}

========================================

{meeting_data.get('transcript', '文字起こしデータがありません')}

========================================

{APP_NAME} システム
生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
生成システム: {APP_NAME} v{APP_VERSION}
"""
            
            # ファイルの書き込み
            with open(txt_filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"文字起こしファイル生成完了: {txt_filepath}")
            return txt_filepath
            
        except Exception as e:
            logger.error(f"文字起こしファイル生成エラー: {str(e)}")
            raise Exception(f"文字起こしファイル生成に失敗しました: {str(e)}")
    
    def _create_markdown_content(self, meeting_data):
        """Markdownコンテンツを作成"""
        meeting_notes = meeting_data.get('meeting_notes', '')
        
        # 議事録の内容のみを返す（ヘッダー情報は除外）
        content = f"""{meeting_notes}

---

## システム情報

- **生成システム**: {APP_NAME} v{APP_VERSION}
- **AIモデル**: Gemini 2.5 Flash
- **生成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        return content
    
    def _format_datetime(self, datetime_str):
        """日時文字列をYYYY/MM/DD HH24:Mi形式に変換"""
        if not datetime_str or datetime_str == '未設定':
            return '未設定'
        
        try:
            # ISO形式の日時をパース
            if 'T' in datetime_str:
                dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            else:
                # その他の形式を試行
                dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            
            # YYYY/MM/DD HH24:Mi形式に変換
            return dt.strftime('%Y/%m/%d %H:%M')
        except ValueError:
            # パースできない場合は元の文字列を返す
            return datetime_str
    
    def _sanitize_filename(self, filename):
        """ファイル名を安全な形式に変換"""
        import re
        # 拡張子を除去
        name = os.path.splitext(filename)[0]
        # 特殊文字を除去
        name = re.sub(r'[^\w\-_\.]', '_', name)
        # 連続するアンダースコアを単一に
        name = re.sub(r'_+', '_', name)
        # 先頭と末尾のアンダースコアを除去
        name = name.strip('_')
        return name
