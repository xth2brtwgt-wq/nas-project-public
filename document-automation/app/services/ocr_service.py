"""
OCR処理サービス（ハイブリッド対応）
"""
from google.cloud import vision
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from config.settings import settings
import os
import logging

logger = logging.getLogger(__name__)


class OCRService:
    """OCR処理のハイブリッドサービス"""
    
    def __init__(self):
        self.use_cloud = settings.ocr_engine == "cloud" and settings.gemini_api_key
        if self.use_cloud:
            try:
                self.vision_client = vision.ImageAnnotatorClient()
                logger.info("Google Cloud Vision API 初期化成功")
            except Exception as e:
                logger.warning(f"Google Cloud Vision API 初期化失敗、ローカルモードにフォールバック: {e}")
                self.use_cloud = False
    
    async def process_document(self, file_path: str) -> dict:
        """
        ドキュメントのOCR処理
        
        Returns:
            {
                "text": str,
                "confidence": float,
                "engine": str,
                "language": str,
                "pages": int
            }
        """
        try:
            file_ext = file_path.split(".")[-1].lower()
            
            # PDF処理
            if file_ext == "pdf":
                return await self._process_pdf(file_path)
            # 画像処理
            else:
                return await self._process_image(file_path)
                
        except Exception as e:
            logger.error(f"OCR処理エラー: {e}")
            raise
    
    async def _process_pdf(self, pdf_path: str) -> dict:
        """PDF処理"""
        try:
            # PDFを画像に変換
            images = convert_from_path(pdf_path, dpi=300)
            
            all_text = []
            confidences = []
            
            for i, image in enumerate(images):
                logger.info(f"PDFページ {i+1}/{len(images)} を処理中...")
                
                # 一時画像保存
                temp_image_path = f"{pdf_path}_page_{i}.png"
                image.save(temp_image_path, "PNG")
                
                # OCR実行
                result = await self._process_image(temp_image_path)
                all_text.append(result["text"])
                confidences.append(result["confidence"])
                
                # 一時ファイル削除
                os.remove(temp_image_path)
            
            return {
                "text": "\n\n--- ページ区切り ---\n\n".join(all_text),
                "confidence": sum(confidences) / len(confidences) if confidences else 0,
                "engine": "cloud" if self.use_cloud else "local",
                "language": settings.ocr_language,
                "pages": len(images)
            }
            
        except Exception as e:
            logger.error(f"PDF処理エラー: {e}")
            raise
    
    async def _process_image(self, image_path: str) -> dict:
        """画像処理"""
        if self.use_cloud:
            return await self._cloud_ocr(image_path)
        else:
            return await self._local_ocr(image_path)
    
    async def _cloud_ocr(self, image_path: str) -> dict:
        """Google Cloud Vision APIでOCR"""
        try:
            with open(image_path, "rb") as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # 日本語対応の設定
            image_context = vision.ImageContext(
                language_hints=settings.ocr_language.split(",")
            )
            
            response = self.vision_client.document_text_detection(
                image=image,
                image_context=image_context
            )
            
            if response.error.message:
                raise Exception(f"Google Vision API エラー: {response.error.message}")
            
            # テキスト抽出
            text = response.full_text_annotation.text if response.full_text_annotation else ""
            
            # 信頼度計算（平均）
            confidences = []
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    confidences.append(block.confidence)
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            logger.info(f"Cloud OCR 成功: {len(text)}文字, 信頼度 {avg_confidence:.2f}")
            
            return {
                "text": text,
                "confidence": avg_confidence,
                "engine": "cloud",
                "language": settings.ocr_language,
                "pages": 1
            }
            
        except Exception as e:
            logger.error(f"Cloud OCR エラー、ローカルにフォールバック: {e}")
            return await self._local_ocr(image_path)
    
    async def _local_ocr(self, image_path: str) -> dict:
        """Tesseract OCRでローカル処理"""
        try:
            image = Image.open(image_path)
            
            # 画像前処理の改善（精度向上のため）
            from PIL import ImageEnhance, ImageFilter
            import numpy as np
            
            # グレースケール変換
            if image.mode != 'L':
                image = image.convert('L')
            
            # ノイズ除去
            image = image.filter(ImageFilter.MedianFilter(size=3))
            
            # コントラスト調整
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)  # コントラストを適度に強化
            
            # シャープネス調整
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)  # シャープネスを強化
            
            # 明度調整
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.1)  # 明度を少し上げる
            
            # Tesseract設定（言語コード変換）
            lang_codes = []
            for lang in settings.ocr_language.split(","):
                if lang.strip() == "ja":
                    lang_codes.append("jpn")
                elif lang.strip() == "en":
                    lang_codes.append("eng")
                else:
                    lang_codes.append(lang.strip())
            lang = "+".join(lang_codes)
            
            # 複数のPSM設定で試行して最良の結果を選択
            psm_configs = [
                r'--oem 3 --psm 1',  # 自動ページセグメンテーション（OSD付き）
                r'--oem 3 --psm 3',  # 完全自動ページセグメンテーション
                r'--oem 3 --psm 4',  # 単一列のテキスト
                r'--oem 3 --psm 6',  # 単一ブロックのテキスト
                r'--oem 3 --psm 8',  # 単一単語
            ]
            
            best_text = ""
            best_confidence = 0
            best_config = ""
            
            for config in psm_configs:
                try:
                    # OCR実行
                    text = pytesseract.image_to_string(image, lang=lang, config=config)
                    
                    # 信頼度取得
                    data = pytesseract.image_to_data(image, lang=lang, config=config, output_type=pytesseract.Output.DICT)
                    confidences = [int(conf) for conf in data['conf'] if conf != '-1']
                    avg_confidence = sum(confidences) / len(confidences) / 100 if confidences else 0
                    
                    # より良い結果を選択（文字数と信頼度の組み合わせ）
                    score = len(text.strip()) * avg_confidence
                    if score > len(best_text.strip()) * best_confidence:
                        best_text = text
                        best_confidence = avg_confidence
                        best_config = config
                        
                except Exception as e:
                    logger.warning(f"PSM設定 {config} でエラー: {e}")
                    continue
            
            text = best_text
            avg_confidence = best_confidence
            
            logger.info(f"Local OCR 成功: {len(text)}文字, 信頼度 {avg_confidence:.2f}, 最適設定: {best_config}")
            
            return {
                "text": text,
                "confidence": avg_confidence,
                "engine": "local",
                "language": settings.ocr_language,
                "pages": 1
            }
            
        except Exception as e:
            logger.error(f"Local OCR エラー: {e}")
            raise

