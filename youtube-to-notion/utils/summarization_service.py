#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
要約生成サービス
Gemini AIを使用した文字起こし・要約生成
meeting-minutes-bycの機能を流用
"""

import os
import logging
import re
import time
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
        
        # リトライ設定
        self.max_retries = 5
        self.base_delay = 2.0  # 基本待機時間（秒）
    
    def _call_with_retry(self, api_call_func, operation_name="API呼び出し"):
        """レート制限エラーに対応したリトライロジック付きAPI呼び出し"""
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                return api_call_func()
            
            except Exception as e:
                error_str = str(e)
                last_error = e
                
                # エラーの詳細情報を取得（可能な限り完全なメッセージを取得）
                error_details = error_str
                if hasattr(e, 'message'):
                    error_details += " " + str(e.message)
                if hasattr(e, 'args') and e.args:
                    for arg in e.args:
                        if isinstance(arg, str) and len(arg) > len(error_details):
                            error_details = arg
                
                # デバッグ用：エラーメッセージ全体をログに記録（INFOレベルで出力）
                logger.info(f"エラー詳細 (試行 {attempt}): {error_str[:500]}")
                if len(error_details) > len(error_str):
                    logger.info(f"エラー詳細（拡張）: {error_details[:500]}")
                # エラーオブジェクトの型と属性も記録
                logger.info(f"エラータイプ: {type(e).__name__}, 属性: {dir(e)[:10]}")
                
                # 429エラー（レート制限）の検出
                is_rate_limit = (
                    "429" in error_str or
                    "quota" in error_str.lower() or
                    "rate limit" in error_str.lower() or
                    "quota exceeded" in error_str.lower()
                )
                
                # 日次クォータ超過（無料枠リミット）の検出
                # この場合はリトライしても意味がないので即座にエラーを返す
                # エラーメッセージ全体をチェック（詳細部分も含む）
                error_full = (error_str + " " + error_details).lower()
                is_daily_quota_exceeded = (
                    "free_tier_requests" in error_full or
                    "free_tier" in error_full or
                    "limit: 50" in error_full or
                    "limit 50" in error_full or
                    ("quota exceeded" in error_full and "free" in error_full) or
                    ("quota exceeded for metric" in error_full and "free" in error_full) or
                    ("you exceeded your current quota" in error_full and ("free" in error_full or "50" in error_full)) or
                    # 429エラー + クォータ超過 + リトライ待機時間が長い（60秒以上）場合は日次クォータ超過と判断
                    ("429" in error_str and "quota" in error_full and "retry" in error_full)
                )
                
                # 日次クォータ超過の場合は即座にエラーを返す（リトライしない）
                if is_daily_quota_exceeded:
                    logger.error(
                        f"{operation_name} - 日次クォータ超過を検出しました。リトライをスキップします。"
                    )
                    raise Exception(
                        f"Gemini APIの無料枠リミット（50リクエスト/日）に達しました。"
                        f"明日（日本時間）に再試行するか、APIプランをアップグレードしてください。"
                    )
                
                # 一時的なレート制限の場合はリトライを試みる
                if is_rate_limit and attempt < self.max_retries:
                    # エラーメッセージからリトライ待機時間を抽出
                    retry_delay = self._extract_retry_delay(error_str, attempt)
                    
                    logger.warning(
                        f"{operation_name} - 一時的なレート制限エラー検出 (試行 {attempt}/{self.max_retries})"
                    )
                    logger.info(f"リトライまで待機: {retry_delay:.2f}秒")
                    logger.info(f"エラー詳細 (試行 {attempt}): {error_str[:500]}")
                    
                    # 早期エラー返却の条件チェック
                    should_abort_early = False
                    abort_reason = ""
                    
                    # デバッグ用：条件チェックの結果をログに記録
                    logger.info(
                        f"{operation_name} - 条件チェック: "
                        f"試行={attempt}, 待機時間={retry_delay:.2f}秒, "
                        f"60秒以上={retry_delay >= 60}, "
                        f"2回目以降50秒以上={attempt >= 2 and retry_delay >= 50}, "
                        f"3回目以降30秒以上={attempt >= 3 and retry_delay >= 30}"
                    )
                    
                    # 長時間待機（60秒以上）の場合は日次クォータ超過の可能性が高い
                    if retry_delay >= 60:
                        should_abort_early = True
                        abort_reason = "長時間の待機が必要です（60秒以上）"
                    
                    # 2回目以降で待機時間が50秒以上の場合は日次クォータ超過と判断
                    elif attempt >= 2 and retry_delay >= 50:
                        should_abort_early = True
                        abort_reason = f"複数回のリトライ後も長時間待機が必要です（試行 {attempt}、待機時間 {retry_delay:.2f}秒）"
                    
                    # 3回目以降で待機時間が30秒以上の場合は日次クォータ超過と判断
                    elif attempt >= 3 and retry_delay >= 30:
                        should_abort_early = True
                        abort_reason = f"複数回のリトライ後も長時間待機が必要です（試行 {attempt}、待機時間 {retry_delay:.2f}秒）"
                    
                    logger.info(f"{operation_name} - 早期中止判定: should_abort_early={should_abort_early}, reason={abort_reason}")
                    
                    if should_abort_early:
                        logger.error(
                            f"{operation_name} - {abort_reason}。"
                            f"日次クォータ超過の可能性が高いため、リトライを中止します。"
                        )
                        raise Exception(
                            f"Gemini APIの無料枠リミット（50リクエスト/日）に達した可能性が高いです。"
                            f"明日（日本時間）に再試行するか、APIプランをアップグレードしてください。"
                        )
                    
                    time.sleep(retry_delay)
                    continue
                
                # レート制限以外のエラー、または最大リトライ回数に達した場合
                if is_rate_limit:
                    logger.error(
                        f"{operation_name} - レート制限エラー: 最大リトライ回数に達しました"
                    )
                    raise Exception(
                        f"{operation_name}に失敗しました: "
                        f"Gemini APIの無料枠リミット（50リクエスト/日）に達した可能性があります。"
                        f"明日再試行するか、APIプランをアップグレードしてください。"
                        f"\n詳細: {error_str[:200]}"
                    )
                else:
                    # レート制限以外のエラーはそのまま再発生
                    raise
        
        # すべてのリトライが失敗した場合（通常は到達しない）
        if last_error:
            raise last_error
    
    def _extract_retry_delay(self, error_str, attempt):
        """エラーメッセージからリトライ待機時間を抽出"""
        # エラーメッセージから秒数を抽出
        # 例: "Please retry in 2.419203029s" または "retry_delay { seconds: 2 }"
        
        # パターン1: "Please retry in X.XXs"
        match = re.search(r"retry in ([\d.]+)s", error_str, re.IGNORECASE)
        if match:
            delay = float(match.group(1))
            # 安全のため、最小2秒、最大60秒に制限
            return max(self.base_delay, min(delay + 1.0, 60.0))
        
        # パターン2: "retry_delay { seconds: X }"
        match = re.search(r"seconds[:\s]+(\d+)", error_str, re.IGNORECASE)
        if match:
            delay = float(match.group(1))
            return max(self.base_delay, min(delay + 1.0, 60.0))
        
        # パターン3: 指数バックオフ（試行回数に応じて待機時間を増やす）
        # デフォルト: 2秒, 4秒, 8秒, 16秒, 32秒
        return self.base_delay * (2 ** (min(attempt, 5) - 1))
    
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
            
            # Gemini APIで文字起こし実行（リトライロジック付き）
            def api_call_primary():
                return self.model.generate_content([
                    prompt,
                    {
                        "mime_type": "audio/mp3",
                        "data": audio_data
                    }
                ])
            
            try:
                response = self._call_with_retry(api_call_primary, "音声文字起こし")
                transcript = response.text.strip()
            except Exception as api_error:
                # 日次クォータ超過の場合は、元のエラーをそのまま伝播
                error_msg = str(api_error)
                if "Gemini APIの無料枠リミット" in error_msg or "日次クォータ超過" in error_msg:
                    raise api_error
                # その他のエラーの場合のみ代替方法を試行
                # エラーの詳細情報を取得
                if hasattr(api_error, 'message'):
                    error_msg += f" | message: {api_error.message}"
                if hasattr(api_error, '__dict__'):
                    error_msg += f" | __dict__: {api_error.__dict__}"
                logger.warning(f"音声処理失敗、代替方法を試行: {error_msg[:500]}")
                
                # 代替方法: ファイルパスを直接指定
                def api_call_fallback():
                    with open(audio_path, 'rb') as f:
                        audio_content = f.read()
                    
                    return self.model.generate_content([
                        prompt,
                        {
                            "mime_type": "audio/mp3", 
                            "data": base64.b64encode(audio_content).decode('utf-8')
                        }
                    ])
                
                try:
                    response = self._call_with_retry(api_call_fallback, "音声文字起こし（代替方法）")
                    transcript = response.text.strip()
                except Exception as fallback_error:
                    logger.error(f"代替方法も失敗: {str(fallback_error)}")
                    # 日次クォータ超過の場合は、元のエラーをそのまま伝播
                    error_msg = str(fallback_error)
                    if "Gemini APIの無料枠リミット" in error_msg or "日次クォータ超過" in error_msg:
                        raise fallback_error
                    raise Exception(f"音声ファイルの処理に失敗しました: {error_msg}")
            
            # ファイル処理完了（アップロードファイルは使用していないため削除不要）
            
            logger.info(f"文字起こし完了: {len(transcript)}文字")
            return transcript
            
        except Exception as e:
            logger.error(f"文字起こしエラー: {str(e)}")
            # 日次クォータ超過の場合は、元のエラーをそのまま伝播
            error_msg = str(e)
            if "Gemini APIの無料枠リミット" in error_msg or "日次クォータ超過" in error_msg:
                raise e
            # その他のエラーの場合は「文字起こしに失敗しました」を追加
            raise Exception(f"文字起こしに失敗しました: {error_msg}")
    
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
            
            # Gemini APIで要約生成（リトライロジック付き）
            def api_call():
                return self.model.generate_content(prompt)
            
            response = self._call_with_retry(api_call, "要約生成")
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
            
            # Gemini APIでコメント分析（リトライロジック付き）
            def api_call():
                return self.model.generate_content(prompt)
            
            response = self._call_with_retry(api_call, "コメント分析")
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
            
            def api_call():
                return self.model.generate_content(prompt)
            
            response = self._call_with_retry(api_call, "キーワード抽出")
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
            
            def api_call():
                return self.model.generate_content(prompt)
            
            response = self._call_with_retry(api_call, "カテゴリ分類")
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
