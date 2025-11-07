#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Drive保存クライアント（Obsidian Vault用）
NAS環境でも動作するようにGoogle Drive APIを使用
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False
    logger.warning("Google Drive APIライブラリがインストールされていません")

# Google Drive APIのスコープ
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class GoogleDriveClient:
    def __init__(self):
        self.folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
        self.credentials_path = os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH', './credentials.json')
        self.token_path = os.getenv('GOOGLE_DRIVE_TOKEN_PATH', './token.json')
        
        self.service = None
        
        if not GOOGLE_DRIVE_AVAILABLE:
            logger.warning("Google Drive APIライブラリが利用できません")
            return
        
        if not self.folder_id:
            logger.warning("Google DriveフォルダIDが設定されていません")
            return
        
        if not os.path.exists(self.credentials_path):
            logger.warning(f"Google Drive認証情報ファイルが見つかりません: {self.credentials_path}")
            logger.info("GOOGLE_DRIVE_SETUP.mdを参照してcredentials.jsonを配置してください")
            return
        
        try:
            self.service = self._get_service()
        except Exception as e:
            logger.warning(f"Google Driveサービスの初期化に失敗: {str(e)}")
    
    def _get_service(self):
        """Google Drive APIサービスを取得"""
        creds = None
        
        # 既存のトークンファイルを確認
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            except Exception as e:
                logger.warning(f"トークンファイルの読み込みに失敗: {str(e)}")
        
        # トークンが無効または存在しない場合は認証フローを実行
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.warning(f"トークンのリフレッシュに失敗: {str(e)}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_path):
                    raise Exception(f"認証情報ファイルが見つかりません: {self.credentials_path}")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # トークンを保存
            try:
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                logger.warning(f"トークンファイルの保存に失敗: {str(e)}")
        
        return build('drive', 'v3', credentials=creds)
    
    def test_connection(self):
        """Google Drive接続テスト"""
        try:
            if not GOOGLE_DRIVE_AVAILABLE:
                return False, "Google Drive APIライブラリがインストールされていません"
            
            if not self.folder_id:
                return False, "Google DriveフォルダIDが設定されていません"
            
            if not self.service:
                return False, "Google Driveサービスが初期化されていません"
            
            # フォルダの存在確認
            try:
                folder = self.service.files().get(
                    fileId=self.folder_id,
                    fields='id,name'
                ).execute()
                
                return True, f"Google Drive接続成功: {folder.get('name', 'Unknown')}"
            except HttpError as e:
                return False, f"Google Drive接続エラー: {str(e)}"
                
        except Exception as e:
            return False, f"Google Drive接続エラー: {str(e)}"
    
    def save_meeting_file(self, meeting_data, markdown_file_path):
        """議事録ファイルをGoogle Driveに保存（議事録のみ）
        
        Args:
            meeting_data: 議事録データ（辞書）
            markdown_file_path: マークダウンファイルのパス
        
        Returns:
            保存されたファイルのID
        """
        try:
            if not self.service:
                raise Exception("Google Driveサービスが初期化されていません")
            
            if not markdown_file_path or not os.path.exists(markdown_file_path):
                raise Exception(f"マークダウンファイルが見つかりません: {markdown_file_path}")
            
            # ファイル名を生成
            meeting_date = meeting_data.get('meeting_date', datetime.now().strftime('%Y-%m-%d'))
            filename = meeting_data.get('filename', 'meeting')
            safe_filename = self._sanitize_filename(filename)
            
            # ファイル名用の日付を生成（Tや:を削除）
            safe_date = self._sanitize_date_for_filename(meeting_date)
            
            # ファイル名を決定（指定フォルダ直下に保存）
            target_filename = f"議事録_{safe_date}_{safe_filename}.md"
            
            # ファイルをアップロード（指定フォルダ直下に保存）
            file_metadata = {
                'name': target_filename,
                'parents': [self.folder_id]  # 指定フォルダ直下に保存
            }
            
            media = MediaFileUpload(
                markdown_file_path,
                mimetype='text/markdown',
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name'
            ).execute()
            
            file_id = file.get('id')
            logger.info(f"Google Driveに保存完了: {file_id} ({target_filename})")
            return file_id
            
        except Exception as e:
            logger.error(f"Google Drive保存エラー: {str(e)}")
            raise Exception(f"Google Drive保存に失敗しました: {str(e)}")
    
    def _get_or_create_folder(self, folder_path: str):
        """指定されたパスのフォルダを作成または取得
        
        Args:
            folder_path: フォルダパス（例: "2024/01/15"）
        
        Returns:
            フォルダID
        """
        try:
            # パスを分割
            path_parts = folder_path.strip('/').split('/')
            current_parent_id = self.folder_id
            
            # 各階層のフォルダを作成または取得
            for folder_name in path_parts:
                if not folder_name:
                    continue
                
                # 既存のフォルダを検索
                existing_folder_id = self._find_folder_by_name(folder_name, current_parent_id)
                
                if existing_folder_id:
                    current_parent_id = existing_folder_id
                else:
                    # フォルダを作成
                    folder_metadata = {
                        'name': folder_name,
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [current_parent_id]
                    }
                    
                    folder = self.service.files().create(
                        body=folder_metadata,
                        fields='id'
                    ).execute()
                    
                    current_parent_id = folder.get('id')
                    logger.info(f"フォルダを作成: {folder_name} ({current_parent_id})")
            
            return current_parent_id
            
        except Exception as e:
            logger.error(f"フォルダの作成/取得エラー: {str(e)}")
            # エラー時はルートフォルダIDを返す
            return self.folder_id
    
    def _find_folder_by_name(self, folder_name: str, parent_id: str) -> Optional[str]:
        """指定された親フォルダ内でフォルダ名で検索
        
        Args:
            folder_name: 検索するフォルダ名
            parent_id: 親フォルダID
        
        Returns:
            フォルダID（見つからない場合はNone）
        """
        try:
            query = f"name='{folder_name}' and parents in '{parent_id}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            
            results = self.service.files().list(
                q=query,
                fields='files(id, name)',
                pageSize=1
            ).execute()
            
            folders = results.get('files', [])
            if folders:
                return folders[0].get('id')
            
            return None
            
        except Exception as e:
            logger.warning(f"フォルダ検索エラー: {str(e)}")
            return None
    
    def _sanitize_filename(self, filename: str) -> str:
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
    
    def _sanitize_date_for_filename(self, date_str: str) -> str:
        """日付文字列をファイル名用に安全な形式に変換
        
        Args:
            date_str: 日付文字列（例: "2025-11-07T06:53:00" または "2025-11-07 06:53:00"）
        
        Returns:
            安全なファイル名用の日付文字列（例: "2025-11-07T065300"）
        """
        import re
        try:
            # スペースをTに変換、:を削除して安全な形式に変換
            # "2025-11-07T06:53:00" -> "2025-11-07T065300"
            # "2025-11-07 06:53:00" -> "2025-11-07T065300"
            safe_date = date_str.replace(' ', 'T').replace(':', '').replace('Z', '')
            # スラッシュやその他の特殊文字を削除（Tとハイフンは残す）
            safe_date = re.sub(r'[^\w\-T]', '', safe_date)
            return safe_date
        except Exception:
            # エラー時は現在日時を使用
            return datetime.now().strftime('%Y-%m-%dT%H%M%S')

