#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion API クライアント
YouTube動画要約のNotion自動投稿機能
meeting-minutes-bycの機能を流用・拡張
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
    
    def create_youtube_page(self, video_info, summary, transcript, comment_analysis=None):
        """YouTube動画要約のNotionページを作成"""
        try:
            if not self.client or not self.database_id:
                raise Exception("Notion設定が不完全です")
            
            
            # 動画のアップロード日を取得
            upload_date = video_info.get('upload_date', '')
            if upload_date:
                try:
                    # アップロード日を日付形式に変換
                    if isinstance(upload_date, str):
                        # YYYYMMDD形式の場合
                        if len(upload_date) == 8:
                            upload_date_obj = datetime.strptime(upload_date, '%Y%m%d')
                        else:
                            # その他の形式の場合は現在日時を使用
                            upload_date_obj = datetime.now()
                    else:
                        upload_date_obj = datetime.now()
                except:
                    upload_date_obj = datetime.now()
            else:
                upload_date_obj = datetime.now()
            
            # ページのプロパティ（既存構造に合わせて調整）
            properties = {
                "ページ": {
                    "title": [
                        {
                            "text": {
                                "content": self._generate_short_title(video_info, summary)
                            }
                        }
                    ]
                },
                "URL": {
                    "url": video_info.get('url', '')
                },
                "読み方": {
                    "rich_text": []
                },
                   "最終更新日時": {
                       "date": {
                           "start": upload_date_obj.strftime('%Y-%m-%d')
                       }
                   }
            }
            
            # タグの設定（YouTubeタグを追加）
            properties["タグ"] = {
                "multi_select": [{"name": "Youtube"}]
            }
            
            logger.info(f"Notionプロパティ設定: {properties}")
            
            # ページの作成
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            page_id = response['id']
            logger.info(f"Notionページ作成完了: {page_id}")
            
            # ページの内容を追加
            self._add_youtube_content(page_id, video_info, summary, transcript, comment_analysis)
            
            # ページURLを生成
            page_url = f"https://notion.so/{page_id.replace('-', '')}"
            
            return page_url
            
        except Exception as e:
            logger.error(f"Notionページ作成エラー: {str(e)}")
            raise Exception(f"Notionページ作成に失敗しました: {str(e)}")
    
    def _add_youtube_content(self, page_id, video_info, summary, transcript, comment_analysis=None):
        """YouTube動画要約の内容をページに追加"""
        try:
            blocks = []
            
            
            # 要約セクション
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "📝 要約"}}
                    ]
                }
            })
            
            # 要約内容を解析してブロック化
            summary_blocks = self._parse_summary_to_blocks(summary)
            blocks.extend(summary_blocks)
            
            # コメント分析セクション
            if comment_analysis and comment_analysis.strip():
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {"type": "text", "text": {"content": "💬 視聴者コメント分析"}}
                        ]
                    }
                })
                
                # コメント分析内容を解析してブロック化
                comment_blocks = self._parse_summary_to_blocks(comment_analysis)
                blocks.extend(comment_blocks)
            
            # 文字起こしセクション（折りたたみ可能）
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "📄 文字起こし全文"}}
                    ]
                }
            })
            
            # 文字起こしをトグルブロックで追加
            transcript_blocks = self._parse_transcript_to_blocks(transcript)
            blocks.extend(transcript_blocks)
            
            # ブロックを追加
            if blocks:
                try:
                    # Notion APIでブロックを追加
                    response = self.client.blocks.children.append(
                        block_id=page_id,
                        children=blocks
                    )
                    logger.info(f"Notionブロック追加完了: {len(blocks)}個のブロック")
                    logger.info(f"Notion API応答: {response}")
                except Exception as api_error:
                    logger.error(f"Notion API呼び出しエラー: {str(api_error)}")
                    # ブロックを個別に追加してみる
                    for i, block in enumerate(blocks):
                        try:
                            self.client.blocks.children.append(
                                block_id=page_id,
                                children=[block]
                            )
                            logger.info(f"ブロック {i+1}/{len(blocks)} 追加完了")
                        except Exception as block_error:
                            logger.error(f"ブロック {i+1} 追加エラー: {str(block_error)}")
            
        except Exception as e:
            logger.error(f"Notionコンテンツ追加エラー: {str(e)}")
            raise Exception(f"Notionコンテンツ追加に失敗しました: {str(e)}")
    
    def _parse_summary_to_blocks(self, summary):
        """要約テキストをNotionブロックに変換"""
        blocks = []
        lines = summary.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 見出しの検出（要約セクションとコメント分析セクションは除外）
            if line.startswith('## '):
                content = line[3:]
                # 要約セクションとコメント分析セクションは除外（重複を防ぐ）
                if '要約' in content or '視聴者コメント分析' in content:
                    continue
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
            # 箇条書きの検出
            elif line.startswith('- '):
                content = line[2:]
                # 長い箇条書きの場合は分割
                if len(content) > 1800:
                    text_chunks = self._split_text_by_length(content, 1800)
                    for chunk in text_chunks:
                        blocks.append({
                            "object": "block",
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {
                                "rich_text": self._parse_inline_formatting(chunk)
                            }
                        })
                else:
                    blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": self._parse_inline_formatting(content)
                        }
                    })
            # 通常の段落
            else:
                # 長い段落の場合は分割
                if len(line) > 1800:
                    text_chunks = self._split_text_by_length(line, 1800)
                    for chunk in text_chunks:
                        blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": self._parse_inline_formatting(chunk)
                            }
                        })
                else:
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": self._parse_inline_formatting(line)
                        }
                    })
        
        return blocks
    
    def _parse_transcript_to_blocks(self, transcript):
        """文字起こしをNotionブロックに変換（折りたたみ可能）"""
        # 文字起こしが長い場合は折りたたみブロックで表示
        if len(transcript) > 1000:
            # テキストを2000文字以内に分割
            text_chunks = self._split_text_by_length(transcript, 1800)
            
            children = []
            for i, chunk in enumerate(text_chunks):
                # チャンクの長さをチェック
                if len(chunk) > 2000:
                    logger.warning(f"チャンク{i}が長すぎます: {len(chunk)}文字")
                    # さらに分割
                    sub_chunks = self._split_text_by_length(chunk, 1500)
                    for j, sub_chunk in enumerate(sub_chunks):
                        children.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {"type": "text", "text": {"content": sub_chunk}}
                                ]
                            }
                        })
                else:
                    children.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {"type": "text", "text": {"content": chunk}}
                            ]
                        }
                    })
            
            return [{
                "object": "block",
                "type": "toggle",
                "toggle": {
                    "rich_text": [
                        {"type": "text", "text": {"content": f"文字起こし全文を表示 ({len(text_chunks)}部分)"}}
                    ],
                    "children": children
                }
            }]
        else:
            return [{
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": transcript}}
                    ]
                }
            }]
    
    def _extract_tags_from_summary(self, summary):
        """要約からタグを抽出"""
        try:
            # タグセクションを検索
            lines = summary.split('\n')
            for line in lines:
                if 'タグ' in line or '🏷️' in line:
                    # タグ部分を抽出
                    tag_text = line.split(':', 1)[-1].strip()
                    if tag_text:
                        tags = [tag.strip() for tag in tag_text.split(',') if tag.strip()]
                        return tags[:5]  # 最大5個
            return []
        except:
            return []
    
    def _get_icon_for_header(self, content):
        """ヘッダーの内容に応じてアイコンを返す"""
        content_lower = content.lower()
        
        if '要約' in content:
            return '📝'
        elif 'キーポイント' in content or 'ポイント' in content:
            return '🎯'
        elif '学んだ' in content or '学習' in content:
            return '📚'
        elif '対象者' in content or 'おすすめ' in content:
            return '👥'
        elif 'タグ' in content:
            return '🏷️'
        else:
            return '📄'
    
    def _split_text_by_length(self, text, max_length):
        """テキストを指定された長さで分割"""
        if len(text) <= max_length:
            return [text]
        
        logger.info(f"テキスト分割開始: 長さ={len(text)}, 最大長={max_length}")
        
        chunks = []
        current_pos = 0
        
        while current_pos < len(text):
            # 最大長で切り取り
            end_pos = current_pos + max_length
            
            if end_pos >= len(text):
                # 最後の部分
                chunk = text[current_pos:]
                chunks.append(chunk)
                logger.info(f"最後のチャンク: 長さ={len(chunk)}")
                break
            
            # 文の境界で分割を試行
            split_pos = end_pos
            for i in range(end_pos, current_pos, -1):
                if text[i] in ['。', '！', '？', '\n', '.', '!', '?']:
                    split_pos = i + 1
                    break
            
            # 文の境界が見つからない場合は単語境界で分割
            if split_pos == end_pos:
                for i in range(end_pos, current_pos, -1):
                    if text[i] in [' ', '　', '、', ',']:
                        split_pos = i + 1
                        break
            
            # それでも見つからない場合は強制分割
            if split_pos == end_pos:
                split_pos = end_pos
            
            chunk = text[current_pos:split_pos]
            chunks.append(chunk)
            logger.info(f"チャンク追加: 長さ={len(chunk)}, 位置={current_pos}-{split_pos}")
            current_pos = split_pos
        
        logger.info(f"テキスト分割完了: {len(chunks)}個のチャンク")
        return chunks
    
    def _generate_short_title(self, video_info, summary):
        """動画タイトルをそのまま使用"""
        try:
            # 動画タイトルをそのまま使用
            title = video_info.get('title', 'YouTube動画要約')
            
            # 長すぎる場合は短縮
            if len(title) <= 50:
                return title
            else:
                return title[:47] + '...'
                
        except Exception as e:
            logger.warning(f"タイトル生成エラー: {str(e)}")
            return "YouTube動画要約"
    
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
