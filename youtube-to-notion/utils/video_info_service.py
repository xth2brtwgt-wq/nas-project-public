#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
動画情報取得サービス
YouTube動画のメタデータを取得・整形
"""

import logging
from datetime import datetime
from utils.youtube_downloader import YouTubeDownloader

logger = logging.getLogger(__name__)

class VideoInfoService:
    def __init__(self):
        self.youtube_downloader = YouTubeDownloader()
    
    def get_video_info(self, video_url):
        """動画情報を取得・整形"""
        try:
            # URL検証
            is_valid, message = self.youtube_downloader.validate_url(video_url)
            if not is_valid:
                raise Exception(message)
            
            # 動画情報取得
            raw_info = self.youtube_downloader.get_video_info(video_url)
            
            # 情報を整形
            formatted_info = self._format_video_info(raw_info)
            
            logger.info(f"動画情報取得成功: {formatted_info['title']}")
            return formatted_info
            
        except Exception as e:
            logger.error(f"動画情報取得エラー: {str(e)}")
            raise Exception(f"動画情報の取得に失敗しました: {str(e)}")
    
    def _format_video_info(self, raw_info):
        """動画情報を整形"""
        # 動画ID抽出
        video_id = self._extract_video_id(raw_info.get('url', ''))
        
        # 再生時間を分:秒形式に変換
        duration_seconds = raw_info.get('duration', 0)
        duration_formatted = self._format_duration(duration_seconds)
        
        # アップロード日を整形
        upload_date = raw_info.get('upload_date', '')
        upload_date_formatted = self._format_upload_date(upload_date)
        
        return {
            'video_id': video_id,
            'title': raw_info.get('title', ''),
            'channel': raw_info.get('channel', ''),
            'duration': duration_seconds,
            'duration_formatted': duration_formatted,
            'thumbnail': raw_info.get('thumbnail', ''),
            'upload_date': upload_date_formatted,
            'description': raw_info.get('description', ''),
            'view_count': raw_info.get('view_count', 0),
            'like_count': raw_info.get('like_count', 0),
            'url': raw_info.get('url', ''),
            'category': self._categorize_video(raw_info),
            'language': self._detect_language(raw_info)
        }
    
    def _extract_video_id(self, url):
        """URLから動画IDを抽出"""
        import re
        
        # 様々なYouTube URL形式に対応
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return ''
    
    def _format_duration(self, seconds):
        """秒数を分:秒形式に変換"""
        if not seconds:
            return '0:00'
        
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        
        if minutes >= 60:
            hours = minutes // 60
            minutes = minutes % 60
            return f"{hours}:{minutes:02d}:{remaining_seconds:02d}"
        else:
            return f"{minutes}:{remaining_seconds:02d}"
    
    def _format_upload_date(self, upload_date):
        """アップロード日を整形"""
        if not upload_date:
            return ''
        
        try:
            # YYYYMMDD形式を日付に変換
            if len(upload_date) == 8:
                date_obj = datetime.strptime(upload_date, '%Y%m%d')
                return date_obj.strftime('%Y年%m月%d日')
            else:
                return upload_date
        except:
            return upload_date
    
    def _categorize_video(self, video_info):
        """動画をカテゴリ分類"""
        title = video_info.get('title', '').lower()
        description = video_info.get('description', '').lower()
        channel = video_info.get('channel', '').lower()
        
        # 技術系キーワード
        tech_keywords = ['python', 'javascript', 'programming', 'coding', '開発', 'プログラミング', '技術', 'ai', '機械学習']
        if any(keyword in title or keyword in description for keyword in tech_keywords):
            return '技術'
        
        # ビジネス系キーワード
        business_keywords = ['business', 'marketing', 'sales', '経営', 'マーケティング', 'ビジネス', '起業']
        if any(keyword in title or keyword in description for keyword in business_keywords):
            return 'ビジネス'
        
        # 教育系キーワード
        education_keywords = ['tutorial', 'lesson', 'learn', 'study', '学習', '教育', 'チュートリアル', '講座']
        if any(keyword in title or keyword in description for keyword in education_keywords):
            return '教育'
        
        # エンタメ系キーワード
        entertainment_keywords = ['music', 'game', 'movie', 'fun', 'entertainment', '音楽', 'ゲーム', '映画', 'エンタメ']
        if any(keyword in title or keyword in description for keyword in entertainment_keywords):
            return 'エンタメ'
        
        return 'その他'
    
    def _detect_language(self, video_info):
        """動画の言語を検出"""
        title = video_info.get('title', '')
        description = video_info.get('description', '')
        
        # 日本語の特徴
        japanese_chars = ['ひらがな', 'カタカナ', '漢字']
        if any(char in title or char in description for char in japanese_chars):
            return 'ja'
        
        # 英語の特徴
        english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        text_lower = (title + ' ' + description).lower()
        if any(word in text_lower for word in english_words):
            return 'en'
        
        return 'unknown'
