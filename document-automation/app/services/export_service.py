"""
エクスポートサービス
"""
from app.models.document import Document
from app.services.ai_service import AIService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def export_to_markdown(document: Document) -> str:
    """
    個別ドキュメントをマークダウンに変換
    """
    lines = [
        f"# {document.original_filename}",
        "",
        "## 基本情報",
        "",
        f"- **ファイル名**: {document.original_filename}",
        f"- **ファイルタイプ**: {document.file_type}",
        f"- **ファイルサイズ**: {document.file_size:,} bytes",
        f"- **処理日時**: {document.processed_at.strftime('%Y-%m-%d %H:%M:%S') if document.processed_at else 'N/A'}",
        f"- **カテゴリ**: {document.category or 'N/A'}",
        "",
        "## 要約",
        "",
        document.summary or "要約なし",
        "",
    ]
    
    # キーワード
    if document.keywords:
        lines.append("## キーワード")
        lines.append("")
        lines.append(", ".join(document.keywords))
        lines.append("")
    
    # 抽出メタデータ
    if document.extracted_metadata:
        lines.append("## 抽出情報")
        lines.append("")
        for key, value in document.extracted_metadata.items():
            lines.append(f"- **{key}**: {value}")
        lines.append("")
    
    # OCRテキスト
    if document.ocr_text:
        lines.append("## 本文")
        lines.append("")
        lines.append(document.ocr_text)
        lines.append("")
    
    # メタ情報
    lines.append("---")
    lines.append("")
    lines.append("### 処理情報")
    lines.append("")
    lines.append(f"- OCRエンジン: {document.ocr_engine or 'N/A'}")
    lines.append(f"- OCR信頼度: {document.ocr_confidence:.2f}" if document.ocr_confidence else "- OCR信頼度: N/A")
    lines.append(f"- 処理時間: {document.processing_time:.2f}秒" if document.processing_time else "- 処理時間: N/A")
    
    return "\n".join(lines)


async def export_summary(documents: list[Document], title: str) -> str:
    """
    複数ドキュメントの統合要約
    """
    try:
        ai_service = AIService()
        
        # ドキュメントデータを準備
        documents_data = [
            {
                "filename": doc.original_filename,
                "summary": doc.summary or "",
                "category": doc.category or "その他",
                "keywords": doc.keywords or [],
                "metadata": doc.extracted_metadata or {}
            }
            for doc in documents
        ]
        
        # AI統合要約生成
        summary_content = await ai_service.generate_combined_summary(documents_data, title)
        
        return summary_content
        
    except Exception as e:
        logger.error(f"統合要約エクスポートエラー: {e}")
        # フォールバック：基本的なまとめ
        return _basic_export_summary(documents, title)


def _basic_export_summary(documents: list[Document], title: str) -> str:
    """基本的な統合要約（フォールバック）"""
    lines = [
        f"# {title}",
        "",
        f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"文書数: {len(documents)}",
        "",
        "## 文書一覧",
        ""
    ]
    
    for i, doc in enumerate(documents, 1):
        lines.append(f"### {i}. {doc.original_filename}")
        lines.append("")
        lines.append(f"- **カテゴリ**: {doc.category or 'N/A'}")
        lines.append(f"- **処理日時**: {doc.processed_at.strftime('%Y-%m-%d %H:%M:%S') if doc.processed_at else 'N/A'}")
        if doc.summary:
            lines.append(f"- **要約**: {doc.summary}")
        if doc.keywords:
            lines.append(f"- **キーワード**: {', '.join(doc.keywords)}")
        lines.append("")
    
    return "\n".join(lines)

