#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
カスタム辞書管理ユーティリティ
音声文字起こしの精度向上のための辞書機能を提供
"""

import json
import os
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class DictionaryManager:
    """カスタム辞書管理クラス"""
    
    def __init__(self, dictionary_path: str = "config/custom_dictionary.json"):
        """
        辞書マネージャーの初期化
        
        Args:
            dictionary_path: 辞書ファイルのパス
        """
        self.dictionary_path = dictionary_path
        self.dictionary_data = self._load_dictionary()
    
    def _load_dictionary(self) -> Dict:
        """辞書ファイルを読み込み"""
        try:
            if os.path.exists(self.dictionary_path):
                with open(self.dictionary_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"辞書ファイルが見つかりません: {self.dictionary_path}")
                return self._create_default_dictionary()
        except Exception as e:
            logger.error(f"辞書ファイルの読み込みに失敗: {str(e)}")
            return self._create_default_dictionary()
    
    def _create_default_dictionary(self) -> Dict:
        """デフォルト辞書を作成"""
        return {
            "version": "1.0.0",
            "description": "音声文字起こし用カスタム辞書",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "categories": {
                "company_names": {
                    "description": "会社名・組織名",
                    "entries": {}
                },
                "technical_terms": {
                    "description": "技術用語",
                    "entries": {}
                },
                "person_names": {
                    "description": "人名",
                    "entries": {}
                },
                "common_phrases": {
                    "description": "よく使われるフレーズ",
                    "entries": {}
                }
            },
            "settings": {
                "case_sensitive": False,
                "partial_match": True,
                "priority_order": ["company_names", "technical_terms", "person_names", "common_phrases"]
            }
        }
    
    def _save_dictionary(self) -> bool:
        """辞書ファイルを保存"""
        try:
            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(self.dictionary_path), exist_ok=True)
            
            # 更新日時を更新
            self.dictionary_data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            
            with open(self.dictionary_path, 'w', encoding='utf-8') as f:
                json.dump(self.dictionary_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"辞書ファイルを保存しました: {self.dictionary_path}")
            return True
        except Exception as e:
            logger.error(f"辞書ファイルの保存に失敗: {str(e)}")
            return False
    
    def get_dictionary_for_prompt(self) -> str:
        """
        文字起こしプロンプト用の辞書情報を取得
        
        Returns:
            プロンプトに組み込む辞書情報の文字列
        """
        if not self.dictionary_data or "categories" not in self.dictionary_data:
            return ""
        
        dictionary_text = "\n## カスタム辞書\n"
        dictionary_text += "以下の用語は正確に文字起こししてください：\n\n"
        
        # 優先順位に従ってカテゴリを処理
        priority_order = self.dictionary_data.get("settings", {}).get("priority_order", [])
        
        for category_name in priority_order:
            if category_name in self.dictionary_data["categories"]:
                category = self.dictionary_data["categories"][category_name]
                entries = category.get("entries", {})
                
                if entries:
                    dictionary_text += f"### {category.get('description', category_name)}\n"
                    for japanese, correct_form in entries.items():
                        dictionary_text += f"- 「{japanese}」→「{correct_form}」\n"
                    dictionary_text += "\n"
        
        return dictionary_text
    
    def add_entry(self, category: str, japanese: str, correct_form: str) -> bool:
        """
        辞書にエントリを追加
        
        Args:
            category: カテゴリ名
            japanese: 日本語表記
            correct_form: 正しい表記
            
        Returns:
            成功した場合True
        """
        try:
            if "categories" not in self.dictionary_data:
                self.dictionary_data["categories"] = {}
            
            if category not in self.dictionary_data["categories"]:
                self.dictionary_data["categories"][category] = {
                    "description": category,
                    "entries": {}
                }
            
            self.dictionary_data["categories"][category]["entries"][japanese] = correct_form
            
            return self._save_dictionary()
        except Exception as e:
            logger.error(f"辞書エントリの追加に失敗: {str(e)}")
            return False
    
    def remove_entry(self, category: str, japanese: str) -> bool:
        """
        辞書からエントリを削除
        
        Args:
            category: カテゴリ名
            japanese: 日本語表記
            
        Returns:
            成功した場合True
        """
        try:
            if (category in self.dictionary_data.get("categories", {}) and
                japanese in self.dictionary_data["categories"][category].get("entries", {})):
                
                del self.dictionary_data["categories"][category]["entries"][japanese]
                return self._save_dictionary()
            
            return False
        except Exception as e:
            logger.error(f"辞書エントリの削除に失敗: {str(e)}")
            return False
    
    def get_all_entries(self) -> Dict:
        """全辞書エントリを取得"""
        return self.dictionary_data.get("categories", {})
    
    def search_entries(self, query: str) -> List[Tuple[str, str, str]]:
        """
        辞書エントリを検索
        
        Args:
            query: 検索クエリ
            
        Returns:
            (カテゴリ, 日本語表記, 正しい表記)のリスト
        """
        results = []
        query_lower = query.lower() if not self.dictionary_data.get("settings", {}).get("case_sensitive", False) else query
        
        for category_name, category_data in self.dictionary_data.get("categories", {}).items():
            for japanese, correct_form in category_data.get("entries", {}).items():
                japanese_lower = japanese.lower() if not self.dictionary_data.get("settings", {}).get("case_sensitive", False) else japanese
                correct_form_lower = correct_form.lower() if not self.dictionary_data.get("settings", {}).get("case_sensitive", False) else correct_form
                
                if (query_lower in japanese_lower or 
                    query_lower in correct_form_lower or
                    (self.dictionary_data.get("settings", {}).get("partial_match", True) and 
                     (japanese_lower in query_lower or correct_form_lower in query_lower))):
                    results.append((category_name, japanese, correct_form))
        
        return results
    
    def get_statistics(self) -> Dict:
        """辞書の統計情報を取得"""
        stats = {
            "total_categories": 0,
            "total_entries": 0,
            "category_breakdown": {}
        }
        
        for category_name, category_data in self.dictionary_data.get("categories", {}).items():
            entry_count = len(category_data.get("entries", {}))
            stats["total_categories"] += 1
            stats["total_entries"] += entry_count
            stats["category_breakdown"][category_name] = entry_count
        
        return stats
    
    def export_dictionary(self, export_path: str) -> bool:
        """
        辞書をエクスポート
        
        Args:
            export_path: エクスポート先パス
            
        Returns:
            成功した場合True
        """
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.dictionary_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"辞書をエクスポートしました: {export_path}")
            return True
        except Exception as e:
            logger.error(f"辞書のエクスポートに失敗: {str(e)}")
            return False
    
    def import_dictionary(self, import_path: str) -> bool:
        """
        辞書をインポート
        
        Args:
            import_path: インポート元パス
            
        Returns:
            成功した場合True
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            # バックアップを作成
            backup_path = f"{self.dictionary_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.export_dictionary(backup_path)
            
            # 辞書を更新
            self.dictionary_data = imported_data
            
            return self._save_dictionary()
        except Exception as e:
            logger.error(f"辞書のインポートに失敗: {str(e)}")
            return False
