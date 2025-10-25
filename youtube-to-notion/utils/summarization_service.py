#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
要約生成サービス
Gemini AIを使用した文字起こし・要約生成
meeting-minutes-bycの機能を流用
"""

import os
import logging
import google.generativeai as genai
from datetime import datetime

logger = logging.getLogger(__name__)

class SummarizationService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            self.model = None
            logger.warning("Gemini API Key not configured")
    
    def transcribe_audio(self, audio_path):
        """音声ファイルを文字起こし"""
        try:
            if not self.model:
                raise Exception("Gemini APIが設定されていません")
            
            logger.info(f"音声文字起こし開始: {audio_path}")
            
            # 文字起こしプロンプト
            prompt = """
            この音声ファイルを正確に文字起こししてください。
            以下の点に注意してください：
            
            1. 話者の発言を正確に聞き取る
            2. 専門用語や固有名詞はそのまま記載
            3. 句読点を適切に配置
            4. 話者の区切りを明確にする
            5. 日本語の場合は敬語や丁寧語も正確に記載
            
            文字起こし結果のみを出力してください。
            """
            
            # 音声ファイルを直接読み込んで処理
            import base64
            with open(audio_path, 'rb') as f:
                audio_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Gemini APIで文字起こし実行
            try:
                response = self.model.generate_content([
                    prompt,
                    {
                        "mime_type": "audio/mp3",
                        "data": audio_data
                    }
                ])
                transcript = response.text.strip()
            except Exception as api_error:
                logger.warning(f"音声処理失敗、代替方法を試行: {str(api_error)}")
                
                # 代替方法: ファイルパスを直接指定
                try:
                    with open(audio_path, 'rb') as f:
                        audio_content = f.read()
                    
                    response = self.model.generate_content([
                        prompt,
                        {
                            "mime_type": "audio/mp3", 
                            "data": base64.b64encode(audio_content).decode('utf-8')
                        }
                    ])
                    transcript = response.text.strip()
                except Exception as fallback_error:
                    logger.error(f"代替方法も失敗: {str(fallback_error)}")
                    raise Exception(f"音声ファイルの処理に失敗しました: {str(fallback_error)}")
            
            # ファイル処理完了（アップロードファイルは使用していないため削除不要）
            
            logger.info(f"文字起こし完了: {len(transcript)}文字")
            return transcript
            
        except Exception as e:
            logger.error(f"文字起こしエラー: {str(e)}")
            raise Exception(f"文字起こしに失敗しました: {str(e)}")
    
    def generate_summary(self, transcript, video_info, comments=None, summary_length='medium'):
        """文字起こしから要約を生成"""
        try:
            if not self.model:
                raise Exception("Gemini APIが設定されていません")
            
            logger.info("要約生成開始")
            
            # 要約長さに応じたプロンプト設定
            length_instructions = {
                'short': '簡潔に（3-5文程度）',
                'medium': '適度に（5-8文程度）',
                'long': '詳細に（8-12文程度）',
                'very_long': '非常に詳細に（12-20文程度）'
            }
            
            length_instruction = length_instructions.get(summary_length, length_instructions['medium'])
            
            # コメント情報を準備
            comments_text = ""
            if comments and len(comments) > 0:
                comments_text = "\n\n視聴者コメント（参考情報）:\n"
                for i, comment in enumerate(comments[:30], 1):  # 上位30件のコメント
                    comments_text += f"{i}. {comment.get('text', '')}\n"
            
            # 要約生成プロンプト
            prompt = f"""
            以下のYouTube動画の文字起こしを分析して、構造化された要約を作成してください。
            
            動画情報:
            - タイトル: {video_info.get('title', '')}
            - チャンネル: {video_info.get('channel', '')}
            - カテゴリ: {video_info.get('category', '')}
            - 言語: {video_info.get('language', '')}
            - 再生時間: {video_info.get('duration', '')}
            
            重要な指示:
            - 「この動画は、」「この動画では、」「動画は、」などの前置詞は一切使用しないでください
            - 動画のURLやリンクは一切含めないでください
            - 要約は1回だけ作成してください（重複しないでください）
            - 動画の内容を直接的に説明してください
            - 要約の冒頭は「動画は、」で始めないでください
            - 英語の動画の場合は、日本語に翻訳して要約してください
            - キーポイントは箇条書き形式で記述してください
            - 視聴者コメントがある場合は、それらも参考にして要約してください
            - 要約の最初に「チャンネル: {video_info.get('channel', '')} | 再生時間: {video_info.get('duration', '')}」を必ず含めてください
            
            要約は以下の形式で出力してください：
            
            ## 📝 要約
            チャンネル: {video_info.get('channel', '')} | 再生時間: {video_info.get('duration', '')}
            
            {length_instruction}の要約文を記載してください。
            
            ## 🎯 キーポイント
            - 重要なポイント1
            - 重要なポイント2
            - 重要なポイント3
            - 重要なポイント4
            - 重要なポイント5
            
            ## 🏷️ タグ
            関連するタグを3-5個記載してください（カンマ区切り）。
            
            文字起こし内容:
            {transcript[:8000]}  # 長すぎる場合は最初の8000文字のみ使用
            {comments_text}
            """
            
            # Gemini APIで要約生成
            response = self.model.generate_content(prompt)
            summary = response.text.strip()
            
            logger.info("要約生成完了")
            return summary
            
        except Exception as e:
            logger.error(f"要約生成エラー: {str(e)}")
            raise Exception(f"要約生成に失敗しました: {str(e)}")
    
    def analyze_comments(self, comments):
        """コメントを分析してサマリーを生成"""
        try:
            if not comments or len(comments) == 0:
                return ""
            
            logger.info(f"コメント分析開始: {len(comments)}件")
            
            # コメントテキストを準備
            comments_text = ""
            for i, comment in enumerate(comments[:50], 1):  # 上位50件のコメント
                author = comment.get('author', '匿名')
                text = comment.get('text', '')
                like_count = comment.get('like_count', 0)
                comments_text += f"{i}. [{author}] {text}"
                if like_count > 0:
                    comments_text += f" (👍{like_count})"
                comments_text += "\n"
            
            # コメント分析プロンプト
            prompt = f"""
            以下のYouTube動画のコメントを分析して、視聴者の反応や意見をまとめてください。
            
            重要な指示:
            - コメントの内容を分析して、視聴者の主な反応や意見をまとめる
            - 肯定的な意見、否定的な意見、質問などを分類する
            - 特に多く言及されている内容やキーワードを抽出する
            - 視聴者の関心が高いポイントを特定する
            
            以下の形式で出力してください：
            
            ## 💬 視聴者コメント分析
            ### 主な反応
            - 肯定的な意見
            - 否定的な意見
            - 質問・疑問点
            
            ### 注目ポイント
            - 多く言及されている内容
            - 視聴者の関心が高いポイント
            
            ### キーワード
            頻出するキーワードや話題
            
            コメント内容:
            {comments_text[:4000]}  # 長すぎる場合は最初の4000文字のみ使用
            """
            
            # Gemini APIでコメント分析
            response = self.model.generate_content(prompt)
            comment_analysis = response.text.strip()
            
            logger.info("コメント分析完了")
            return comment_analysis
            
        except Exception as e:
            logger.warning(f"コメント分析エラー: {str(e)}")
            return ""
    
    def extract_keywords(self, transcript, video_info):
        """キーワード抽出"""
        try:
            if not self.model:
                return []
            
            prompt = f"""
            以下の動画内容から重要なキーワードを10個抽出してください。
            
            動画タイトル: {video_info.get('title', '')}
            文字起こし: {transcript[:4000]}
            
            キーワードをカンマ区切りで出力してください。
            """
            
            response = self.model.generate_content(prompt)
            keywords_text = response.text.strip()
            
            # カンマ区切りで分割してリスト化
            keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
            
            return keywords[:10]  # 最大10個
            
        except Exception as e:
            logger.error(f"キーワード抽出エラー: {str(e)}")
            return []
    
    def categorize_content(self, transcript, video_info):
        """コンテンツのカテゴリ分類"""
        try:
            if not self.model:
                return video_info.get('category', 'その他')
            
            prompt = f"""
            以下の動画内容を分析して、最も適切なカテゴリを選択してください。
            
            動画タイトル: {video_info.get('title', '')}
            文字起こし: {transcript[:4000]}
            
            選択肢: 技術, ビジネス, 教育, エンタメ, その他
            
            カテゴリ名のみを出力してください。
            """
            
            response = self.model.generate_content(prompt)
            category = response.text.strip()
            
            # 有効なカテゴリかチェック
            valid_categories = ['技術', 'ビジネス', '教育', 'エンタメ', 'その他']
            if category in valid_categories:
                return category
            else:
                return video_info.get('category', 'その他')
                
        except Exception as e:
            logger.error(f"カテゴリ分類エラー: {str(e)}")
            return video_info.get('category', 'その他')
