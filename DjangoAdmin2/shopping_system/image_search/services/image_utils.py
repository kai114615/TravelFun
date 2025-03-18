import os
import numpy as np
from PIL import Image
import imagehash
import logging
from typing import Optional, Tuple, Dict, Any

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageFingerprint:
    """圖片指紋計算工具類，用於精確識別相同或極度相似的圖片"""
    
    @staticmethod
    def calculate_phash(image_path: str) -> Optional[str]:
        """
        計算圖片的感知哈希值
        
        Args:
            image_path: 圖片路徑或URL
            
        Returns:
            感知哈希值的十六進制字符串，失敗時返回None
        """
        try:
            # 本地路徑
            if os.path.exists(image_path):
                img = Image.open(image_path).convert("RGB")
            # URL路徑
            elif image_path.startswith(('http://', 'https://')):
                import requests
                from io import BytesIO
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                }
                
                response = requests.get(image_path, timeout=10, headers=headers)
                if response.status_code != 200:
                    logger.error(f"下載圖片失敗: {image_path}, 狀態碼: {response.status_code}")
                    return None
                    
                img = Image.open(BytesIO(response.content)).convert("RGB")
            else:
                logger.error(f"無效的圖片路徑: {image_path}")
                return None
                
            # 計算感知哈希值
            phash = imagehash.phash(img)
            return str(phash)
            
        except Exception as e:
            logger.exception(f"計算圖片指紋時出錯: {str(e)}")
            return None
    
    @staticmethod
    def hamming_distance(hash1: str, hash2: str) -> int:
        """
        計算兩個哈希值的漢明距離
        
        Args:
            hash1: 第一個哈希值
            hash2: 第二個哈希值
            
        Returns:
            漢明距離，0表示完全相同
        """
        if len(hash1) != len(hash2):
            raise ValueError("哈希值長度不同")
            
        # 計算不同位的數量
        return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
    
    @staticmethod
    def is_same_image(hash1: str, hash2: str, threshold: int = 5) -> bool:
        """
        判斷兩張圖片是否為同一張圖片
        
        Args:
            hash1: 第一個圖片的哈希值
            hash2: 第二個圖片的哈希值
            threshold: 閾值，漢明距離小於此值被認為是同一張圖片
            
        Returns:
            是否為同一張圖片
        """
        try:
            distance = ImageFingerprint.hamming_distance(hash1, hash2)
            return distance <= threshold
        except Exception as e:
            logger.exception(f"比較圖片指紋時出錯: {str(e)}")
            return False
            
    @staticmethod
    def detect_duplicate_images(query_image_path: str, target_urls: list) -> Dict[str, Any]:
        """
        檢測目標URL列表中與查詢圖片相同的圖片
        
        Args:
            query_image_path: 查詢圖片路徑
            target_urls: 目標圖片URL列表
            
        Returns:
            包含重複檢測結果的字典
        """
        result = {
            'has_duplicates': False,
            'duplicate_urls': [],
            'duplicate_indices': [],
            'error': None
        }
        
        try:
            # 計算查詢圖片的哈希值
            query_hash = ImageFingerprint.calculate_phash(query_image_path)
            if not query_hash:
                result['error'] = "無法計算查詢圖片的指紋"
                return result
                
            # 檢查每個目標URL
            for i, url in enumerate(target_urls):
                if not url:
                    continue
                    
                target_hash = ImageFingerprint.calculate_phash(url)
                if not target_hash:
                    continue
                    
                if ImageFingerprint.is_same_image(query_hash, target_hash):
                    result['has_duplicates'] = True
                    result['duplicate_urls'].append(url)
                    result['duplicate_indices'].append(i)
                    
            return result
                
        except Exception as e:
            result['error'] = str(e)
            logger.exception(f"檢測重複圖片時出錯: {str(e)}")
            return result 