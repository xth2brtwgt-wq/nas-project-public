#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion API クライアント
"""

import os
import logging
import re
from datetime import datetime, timedelta, timezone
from notion_client import Client

logger = logging.getLogger(__name__)

class NotionClient:
    def __init__(self):
        self.notion_api_key = os.getenv('NOTION_API_KEY')
        self.database_id = os.getenv('NOTION_DATABASE_ID')
        
        if self.notion_api_key:
            self.client = Client(auth=self.notion_api_key)
        else:
            self.client = None
            logger.warning("Notion API Key not configured")
    
    def test_connection(self):
        """Notion接続テスト"""
        try:
            if not self.client or not self.database_id:
                return False, "Notion設定が不完全です"
            
            # データベースの情報を取得
            database = self.client.databases.retrieve(database_id=self.database_id)
            return True, f"Notion接続成功: {database.get('title', [{}])[0].get('plain_text', 'Unknown')}"
        except Exception as e:
            return False, f"Notion接続エラー: {str(e)}"
    
    def create_meeting_page(self, meeting_data):
        """Notionに議事録ページを作成"""
        try:
            if not self.client or not self.database_id:
                raise Exception("Notion設定が不完全です")
            
            # 日時形式を変換
            formatted_meeting_date = self._format_datetime_for_notion(meeting_data.get('meeting_date', ''))
            
            # 議事録のタイトル
            title = f"議事録 - {formatted_meeting_date}"
            
            # ページのプロパティ
            properties = {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                "WaveFile": {
                    "rich_text": [
                        {
                            "text": {
                                "content": meeting_data.get('filename', '不明')
                            }
                        }
                    ]
                }
            }
            
            # 日時プロパティの追加
            meeting_date = meeting_data.get('meeting_date', '')
            if meeting_date and meeting_date.strip():
                try:
                    if 'T' in meeting_date:
                        dt = datetime.fromisoformat(meeting_date.replace('Z', '+00:00'))
                    else:
                        dt = datetime.strptime(meeting_date, '%Y-%m-%d %H:%M:%S')
                    
                    jst = timezone(timedelta(hours=9))
                    dt_jst = dt.replace(tzinfo=jst)
                    iso_date = dt_jst.isoformat()
                    
                    properties["MeetingDate"] = {
                        "date": {
                            "start": iso_date
                        }
                    }
                except ValueError:
                    jst = timezone(timedelta(hours=9))
                    dt_jst = datetime.now(jst)
                    properties["MeetingDate"] = {
                        "date": {
                            "start": dt_jst.isoformat()
                        }
                    }
            else:
                jst = timezone(timedelta(hours=9))
                dt_jst = datetime.now(jst)
                properties["MeetingDate"] = {
                    "date": {
                        "start": dt_jst.isoformat()
                    }
                }
            
            # 作成日時は常に現在時刻（日本時間）
            jst = timezone(timedelta(hours=9))
            dt_jst = datetime.now(jst)
            properties["CreationDate"] = {
                "date": {
                    "start": dt_jst.isoformat()
                }
            }
            
            # ページの作成
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            page_id = response['id']
            logger.info(f"Notionページ作成完了: {page_id}")
            
            # ページの内容を追加
            self._add_page_content(page_id, meeting_data.get('meeting_notes', ''))
            
            return page_id
            
        except Exception as e:
            logger.error(f"Notionページ作成エラー: {str(e)}")
            raise Exception(f"Notionページ作成に失敗しました: {str(e)}")
    
    def _add_page_content(self, page_id, markdown_content):
        """ページの内容を追加"""
        try:
            # MarkdownをNotionブロックに変換
            blocks = self._parse_markdown_to_notion_blocks(markdown_content)
            
            # ブロックを追加
            if blocks:
                self.client.blocks.children.append(
                    block_id=page_id,
                    children=blocks
                )
                logger.info(f"Notionブロックバッチ追加完了: {len(blocks)}個のブロック")
            
            logger.info(f"Notionページ内容追加完了: {page_id}")
            
        except Exception as e:
            logger.error(f"Notionページ内容追加エラー: {str(e)}")
            raise Exception(f"Notionページ内容追加に失敗しました: {str(e)}")
    
    def _parse_markdown_to_notion_blocks(self, markdown_text):
        """MarkdownテキストをNotionのブロック構造に変換（アイコン付きヘッダー対応）"""
        blocks = []
        lines = markdown_text.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped_line = line.strip()
            
            # 空行はスキップ
            if not stripped_line:
                i += 1
                continue
            
            # インデントレベルを計算（スペース4つで1レベル）
            indent_level = (len(line) - len(line.lstrip())) // 4
            
            # 見出し1（アイコン付き）
            if stripped_line.startswith('# ') and not stripped_line.startswith('## '):
                content = stripped_line[2:]
                icon = self._get_icon_for_header(content)
                blocks.append({
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [
                            {"type": "text", "text": {"content": f"{icon} {content}"}}
                        ]
                    }
                })
                i += 1
            
            # 見出し2（アイコン付き）
            elif stripped_line.startswith('## '):
                content = stripped_line[3:]
                icon = self._get_icon_for_header(content)
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {"type": "text", "text": {"content": f"{icon} {content}"}}
                        ]
                    }
                })
                i += 1
            
            # 番号付きリスト（トップレベルのみ）
            elif re.match(r'^\d+\.\s+', stripped_line) and indent_level == 0:
                content = re.sub(r'^\d+\.\s+', '', stripped_line)
                block = {
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "rich_text": self._parse_inline_formatting(content)
                    }
                }
                
                # 次の行から子要素を収集
                i += 1
                children = []
                while i < len(lines):
                    child_line = lines[i]
                    child_stripped = child_line.strip()
                    child_indent = (len(child_line) - len(child_line.lstrip())) // 4
                    
                    # 空行はスキップ
                    if not child_stripped:
                        i += 1
                        continue
                    
                    # インデントが浅くなったら終了
                    if child_indent == 0:
                        break
                    
                    # 1レベル深い箇条書き
                    if child_indent == 1 and child_stripped.startswith('- '):
                        child_content = child_stripped[2:]
                        children.append({
                            "object": "block",
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {
                                "rich_text": self._parse_inline_formatting(child_content)
                            }
                        })
                        i += 1
                    # 1レベル深い番号付きリスト
                    elif child_indent == 1 and re.match(r'^\d+\.\s+', child_stripped):
                        child_content = re.sub(r'^\d+\.\s+', '', child_stripped)
                        children.append({
                            "object": "block",
                            "type": "numbered_list_item",
                            "numbered_list_item": {
                                "rich_text": self._parse_inline_formatting(child_content)
                            }
                        })
                        i += 1
                    else:
                        # それ以外はスキップ（または段落として追加）
                        i += 1
                
                # 子要素がある場合は追加
                if children:
                    block["numbered_list_item"]["children"] = children
                
                blocks.append(block)
            
            # 箇条書きリスト（通常の箇条書き）
            elif stripped_line.startswith('- '):
                content = stripped_line[2:]
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": self._parse_inline_formatting(content)
                    }
                })
                i += 1
            
            # 水平線
            elif stripped_line == '---':
                blocks.append({"object": "block", "type": "divider", "divider": {}})
                i += 1
            
            # 通常の段落
            else:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": self._parse_inline_formatting(stripped_line)}
                })
                i += 1
        
        return blocks
    
    def _get_icon_for_header(self, content):
        """ヘッダーの内容に応じてアイコンを返す"""
        content_lower = content.lower()
        
        if 'エグゼクティブサマリー' in content or '概要' in content:
            return '📋'
        elif '主要な議題' in content or '議題' in content:
            return '📝'
        elif 'アクション' in content or 'タスク' in content:
            return '✅'
        elif '決定事項' in content:
            return '🎯'
        elif '課題' in content or '懸念' in content:
            return '⚠️'
        elif '備考' in content or 'その他' in content:
            return '📌'
        elif '日時' in content or '時間' in content:
            return '📅'
        elif '参加者' in content:
            return '👥'
        else:
            return '📄'
    
    def _parse_inline_formatting(self, text):
        """太字、斜体などのインライン書式を解析してrich_text形式に変換"""
        rich_text = []
        current_pos = 0
        
        # **太字**のパターンを検出
        bold_pattern = r'\*\*(.+?)\*\*'
        
        parts = re.split(bold_pattern, text)
        
        for i, part in enumerate(parts):
            if not part:
                continue
            
            # 奇数インデックスは太字部分
            if i % 2 == 1:
                rich_text.append({
                    "type": "text",
                    "text": {"content": part},
                    "annotations": {"bold": True}
                })
            else:
                # 通常のテキスト
                if part:
                    rich_text.append({
                        "type": "text",
                        "text": {"content": part}
                    })
        
        return rich_text if rich_text else [{"type": "text", "text": {"content": text}}]
    
    def _format_datetime_for_notion(self, datetime_str):
        """日時文字列をNotion用の形式に変換"""
        if not datetime_str or datetime_str == '未設定':
            return '未設定'
        
        try:
            if 'T' in datetime_str:
                dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            
            return dt.strftime('%Y/%m/%d %H:%M')
        except ValueError:
            return datetime_str
