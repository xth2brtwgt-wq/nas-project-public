#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
議事録テンプレート管理機能
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class TemplateManager:
    def __init__(self):
        self.templates_dir = os.getenv('TEMPLATES_DIR', './templates')
        self.templates_file = os.path.join(self.templates_dir, 'meeting_templates.json')
        self._ensure_templates_dir()
        self._initialize_default_templates()
    
    def _ensure_templates_dir(self):
        """テンプレートディレクトリの作成"""
        os.makedirs(self.templates_dir, exist_ok=True)
    
    def _initialize_default_templates(self):
        """デフォルトテンプレートの初期化"""
        if not os.path.exists(self.templates_file):
            default_templates = self._get_default_templates()
            self._save_templates(default_templates)
            logger.info("デフォルトテンプレートを初期化しました")
    
    def _get_default_templates(self) -> Dict:
        """デフォルトテンプレートの定義"""
        return {
            "templates": {
                "standard": {
                    "id": "standard",
                    "name": "標準議事録",
                    "description": "一般的な会議に適した標準的な議事録テンプレート",
                    "prompt_template": """
あなたは経験豊富なエグゼクティブアシスタントとして、バーチャル会議の記録を個人用の構造化された議事録に変換する専門家です。

## あなたの役割と目的
- 主な目的は、バーチャル会議の記録を個人用の構造化された議事録に変換し、効率的なレビューとフォローアップを可能にすることです
- 明確で簡潔かつ実行可能な議事録を作成し、重要なテーマを特定し、コミットメントを追跡します
- 記録を分析して主要なトピックを理解し、重要な議論ポイントと決定事項を抽出し、すべてのアクション項目と担当者、期限を特定します

## 対象読者
効果的な情報管理と責任追跡のために簡潔で整理された会議ノートを必要とする忙しいプロフェッショナル

## 出力要件
- プロフェッショナルで構造化されたトーンを維持
- 箇条書きと太字のヘッダーを使用して読みやすさを高める
- エグゼクティブサマリー、ユーザーの主要なアクション項目/コミットメント、トピックごとの詳細な内訳の3つのセクションに整理

文字起こし内容：
{transcript}
{conditions_text}
{meeting_date_text}

以下の形式で議事録を作成してください：

# 会議議事録

## エグゼクティブサマリー
- **日時**: {formatted_meeting_date}
- **参加者**: [参加者名]
- **主要議題**: [主要な議題の概要]
- **重要決定事項**: [最も重要な決定事項を3つ以内で要約]

## 主要な議題・トピック
1. **[議題1]**
   - **内容**: [詳細な議論内容]
   - **決定事項**: [決定内容]
   - **重要なポイント**: [特に重要な議論ポイント]

2. **[議題2]**
   - **内容**: [詳細な議論内容]
   - **決定事項**: [決定内容]
   - **重要なポイント**: [特に重要な議論ポイント]

3. **[議題3]**
   - **内容**: [詳細な議論内容]
   - **決定事項**: [決定内容]
   - **重要なポイント**: [特に重要な議論ポイント]

## ユーザーの主要なアクション項目・コミットメント
- **[担当者]**: [タスク内容] - **期限**: [期限]
- **[担当者]**: [タスク内容] - **期限**: [期限]
- **[担当者]**: [タスク内容] - **期限**: [期限]

## 決定事項サマリー
- [決定事項1]
- [決定事項2]
- [決定事項3]

## 次回までの課題・懸念事項
- [課題1]
- [課題2]
- [課題3]

## 備考・その他の重要な情報
[その他の重要な情報、補足事項、次回会議への引き継ぎ事項]

**重要**: 
- 議題・トピックの番号は必ず1から順番に連番で記載してください(1. 2. 3. 4. ...)
- 文字起こし内容から複数の議題を抽出し、それぞれに適切な番号を付けてください
- 同じ番号を複数回使用しないでください
- 太字のヘッダーを使用して構造化し、読みやすさを重視してください
- 例：1. 議題A、2. 議題B、3. 議題C のように連番で記載
""",
                    "created_at": datetime.now().isoformat(),
                    "is_default": True
                },
                "concise": {
                    "id": "concise",
                    "name": "簡潔版議事録",
                    "description": "要点を簡潔にまとめた議事録テンプレート",
                    "prompt_template": """
あなたは経験豊富なアシスタントとして、会議の記録を簡潔で実用的な議事録に変換する専門家です。

文字起こし内容：
{transcript}
{conditions_text}
{meeting_date_text}

以下の簡潔な形式で議事録を作成してください：

# 会議議事録

## 基本情報
- **日時**: {formatted_meeting_date}
- **参加者**: [参加者名]
- **主要議題**: [主要な議題]

## 決定事項
- [決定事項1]
- [決定事項2]
- [決定事項3]

## アクションアイテム
- **[担当者]**: [タスク] - **期限**: [期限]
- **[担当者]**: [タスク] - **期限**: [期限]

## 次回までの課題
- [課題1]
- [課題2]

**重要**: 
- 簡潔で読みやすい形式を心がけてください
- 重要なポイントのみを抽出してください
- 箇条書きを活用して整理してください
""",
                    "created_at": datetime.now().isoformat(),
                    "is_default": True
                },
                "detailed": {
                    "id": "detailed",
                    "name": "詳細版議事録",
                    "description": "詳細な分析と背景情報を含む包括的な議事録テンプレート",
                    "prompt_template": """
あなたは経験豊富なビジネスアナリストとして、会議の記録を詳細で包括的な議事録に変換する専門家です。

文字起こし内容：
{transcript}
{conditions_text}
{meeting_date_text}

以下の詳細な形式で議事録を作成してください：

# 会議議事録

## 会議概要
- **日時**: {formatted_meeting_date}
- **参加者**: [参加者名と役職]
- **会議形式**: [対面/オンライン/ハイブリッド]
- **会議時間**: [開始時刻 - 終了時刻]

## エグゼクティブサマリー
- **主要目的**: [会議の主な目的]
- **重要決定事項**: [最も重要な決定事項を3つ以内で要約]
- **主要成果**: [会議で得られた主要な成果]

## 議題別詳細分析

### 1. [議題1]
- **背景・経緯**: [議題の背景と経緯]
- **議論内容**: [詳細な議論内容]
- **提案・意見**: [出された提案や意見]
- **決定事項**: [決定内容と理由]
- **今後の方針**: [今後の対応方針]

### 2. [議題2]
- **背景・経緯**: [議題の背景と経緯]
- **議論内容**: [詳細な議論内容]
- **提案・意見**: [出された提案や意見]
- **決定事項**: [決定内容と理由]
- **今後の方針**: [今後の対応方針]

### 3. [議題3]
- **背景・経緯**: [議題の背景と経緯]
- **議論内容**: [詳細な議論内容]
- **提案・意見**: [出された提案や意見]
- **決定事項**: [決定内容と理由]
- **今後の方針**: [今後の対応方針]

## アクションアイテム詳細
| 担当者 | タスク内容 | 期限 | 優先度 | 備考 |
|--------|------------|------|--------|------|
| [担当者1] | [タスク1] | [期限1] | [優先度1] | [備考1] |
| [担当者2] | [タスク2] | [期限2] | [優先度2] | [備考2] |

## リスク・課題分析
- **特定されたリスク**: [リスク1, リスク2, リスク3]
- **対策**: [各リスクに対する対策]
- **懸念事項**: [継続的な懸念事項]

## 次回会議への引き継ぎ
- **次回会議予定**: [日時・場所]
- **準備事項**: [次回までに準備すべき事項]
- **確認事項**: [次回確認すべき事項]

## 補足情報・備考
[その他の重要な情報、補足事項、参考資料等]

**重要**: 
- 各議題について背景から決定事項まで体系的に整理してください
- アクションアイテムは表形式で明確に整理してください
- リスクや課題についても詳細に分析してください
""",
                    "created_at": datetime.now().isoformat(),
                    "is_default": True
                }
            },
            "default_template": "standard",
            "last_updated": datetime.now().isoformat()
        }
    
    def get_all_templates(self) -> Dict:
        """すべてのテンプレートを取得"""
        try:
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"テンプレート読み込みエラー: {str(e)}")
            return self._get_default_templates()
    
    def get_template(self, template_id: str) -> Optional[Dict]:
        """指定されたテンプレートを取得"""
        templates_data = self.get_all_templates()
        return templates_data.get('templates', {}).get(template_id)
    
    def get_default_template_id(self) -> str:
        """デフォルトテンプレートIDを取得"""
        templates_data = self.get_all_templates()
        return templates_data.get('default_template', 'standard')
    
    def get_template_list(self) -> List[Dict]:
        """テンプレート一覧を取得（UI表示用）"""
        templates_data = self.get_all_templates()
        templates = templates_data.get('templates', {})
        
        template_list = []
        for template_id, template_data in templates.items():
            template_list.append({
                'id': template_id,
                'name': template_data.get('name', ''),
                'description': template_data.get('description', ''),
                'is_default': template_data.get('is_default', False),
                'created_at': template_data.get('created_at', '')
            })
        
        return template_list
    
    def add_custom_template(self, template_id: str, name: str, description: str, prompt_template: str) -> bool:
        """カスタムテンプレートを追加"""
        try:
            templates_data = self.get_all_templates()
            
            # 新しいテンプレートを追加
            templates_data['templates'][template_id] = {
                'id': template_id,
                'name': name,
                'description': description,
                'prompt_template': prompt_template,
                'created_at': datetime.now().isoformat(),
                'is_default': False
            }
            
            # ファイルに保存
            self._save_templates(templates_data)
            logger.info(f"カスタムテンプレートを追加しました: {template_id}")
            return True
            
        except Exception as e:
            logger.error(f"カスタムテンプレート追加エラー: {str(e)}")
            return False
    
    def update_template(self, template_id: str, name: str = None, description: str = None, prompt_template: str = None) -> bool:
        """テンプレートを更新"""
        try:
            templates_data = self.get_all_templates()
            
            if template_id not in templates_data.get('templates', {}):
                logger.error(f"テンプレートが見つかりません: {template_id}")
                return False
            
            # デフォルトテンプレートは更新不可
            if templates_data['templates'][template_id].get('is_default', False):
                logger.warning(f"デフォルトテンプレートは更新できません: {template_id}")
                return False
            
            # 更新
            if name is not None:
                templates_data['templates'][template_id]['name'] = name
            if description is not None:
                templates_data['templates'][template_id]['description'] = description
            if prompt_template is not None:
                templates_data['templates'][template_id]['prompt_template'] = prompt_template
            
            templates_data['templates'][template_id]['updated_at'] = datetime.now().isoformat()
            
            # ファイルに保存
            self._save_templates(templates_data)
            logger.info(f"テンプレートを更新しました: {template_id}")
            return True
            
        except Exception as e:
            logger.error(f"テンプレート更新エラー: {str(e)}")
            return False
    
    def delete_template(self, template_id: str) -> bool:
        """テンプレートを削除"""
        try:
            templates_data = self.get_all_templates()
            
            if template_id not in templates_data.get('templates', {}):
                logger.error(f"テンプレートが見つかりません: {template_id}")
                return False
            
            # デフォルトテンプレートは削除不可
            if templates_data['templates'][template_id].get('is_default', False):
                logger.warning(f"デフォルトテンプレートは削除できません: {template_id}")
                return False
            
            # デフォルトテンプレートを削除しようとしている場合は、別のテンプレートに変更
            if templates_data.get('default_template') == template_id:
                # 最初のデフォルトテンプレートに変更
                for tid, tdata in templates_data['templates'].items():
                    if tdata.get('is_default', False) and tid != template_id:
                        templates_data['default_template'] = tid
                        break
            
            # テンプレートを削除
            del templates_data['templates'][template_id]
            
            # ファイルに保存
            self._save_templates(templates_data)
            logger.info(f"テンプレートを削除しました: {template_id}")
            return True
            
        except Exception as e:
            logger.error(f"テンプレート削除エラー: {str(e)}")
            return False
    
    def set_default_template(self, template_id: str) -> bool:
        """デフォルトテンプレートを設定"""
        try:
            templates_data = self.get_all_templates()
            
            if template_id not in templates_data.get('templates', {}):
                logger.error(f"テンプレートが見つかりません: {template_id}")
                return False
            
            templates_data['default_template'] = template_id
            self._save_templates(templates_data)
            logger.info(f"デフォルトテンプレートを設定しました: {template_id}")
            return True
            
        except Exception as e:
            logger.error(f"デフォルトテンプレート設定エラー: {str(e)}")
            return False
    
    def _save_templates(self, templates_data: Dict):
        """テンプレートデータをファイルに保存"""
        templates_data['last_updated'] = datetime.now().isoformat()
        with open(self.templates_file, 'w', encoding='utf-8') as f:
            json.dump(templates_data, f, ensure_ascii=False, indent=2)
    
    def generate_meeting_notes_with_template(self, template_id: str, transcript: str, conditions: str = "", meeting_date: str = "", participants: str = "") -> str:
        """指定されたテンプレートを使用して議事録を生成"""
        template = self.get_template(template_id)
        if not template:
            logger.error(f"テンプレートが見つかりません: {template_id}")
            # デフォルトテンプレートを使用
            template = self.get_template(self.get_default_template_id())
        
        # テンプレート変数の準備
        conditions_text = f"\n\n追加条件: {conditions}" if conditions else ""
        meeting_date_text = f"\n\n会議日時: {meeting_date}" if meeting_date else ""
        participants_text = f"\n\n参加者: {participants}" if participants else ""
        
        # 日時形式を変換
        from datetime import datetime
        if meeting_date and meeting_date.strip():
            try:
                if 'T' in meeting_date:
                    dt = datetime.fromisoformat(meeting_date.replace('Z', '+00:00'))
                else:
                    dt = datetime.strptime(meeting_date, '%Y-%m-%d %H:%M:%S')
                formatted_meeting_date = dt.strftime('%Y/%m/%d %H:%M')
            except ValueError:
                formatted_meeting_date = meeting_date
        else:
            formatted_meeting_date = datetime.now().strftime('%Y/%m/%d %H:%M')
        
        # テンプレートに変数を適用
        prompt = template['prompt_template'].format(
            transcript=transcript,
            conditions_text=conditions_text,
            meeting_date_text=meeting_date_text,
            participants_text=participants_text,
            formatted_meeting_date=formatted_meeting_date
        )
        
        return prompt
