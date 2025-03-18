import os
import numpy as np
from PIL import Image
import imagehash
import logging
from typing import Optional, Dict, Any

# 從現有的 image_utils 導入 ImageFingerprint 類
from .image_utils import ImageFingerprint

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageFingerprintService:
    """
    圖片指紋服務類，提供圖片指紋計算和比較功能
    封裝 ImageFingerprint 類的功能，並提供更高級的接口
    """
    
    def __init__(self):
        """初始化指紋服務"""
        logger.info("初始化圖片指紋服務")
    
    def get_image_fingerprint(self, image_path: str) -> Optional[str]:
        """
        獲取圖片的指紋哈希值
        
        Args:
            image_path: 圖片路徑或URL
            
        Returns:
            圖片的指紋哈希值，失敗時返回None
        """
        return ImageFingerprint.calculate_phash(image_path)
    
    def compare_fingerprints(self, fingerprint1: str, fingerprint2: str) -> int:
        """
        比較兩個指紋的差異度
        
        Args:
            fingerprint1: 第一個指紋哈希值
            fingerprint2: 第二個指紋哈希值
            
        Returns:
            漢明距離，0表示完全相同，值越小表示越相似
        """
        if not fingerprint1 or not fingerprint2:
            logger.warning("比較指紋時發現無效的指紋值")
            return 100  # 返回一個較大的值表示差異很大
            
        try:
            return ImageFingerprint.hamming_distance(fingerprint1, fingerprint2)
        except Exception as e:
            logger.error(f"比較指紋時出錯: {str(e)}")
            return 100
    
    def is_similar_image(self, fingerprint1: str, fingerprint2: str, threshold: int = 5) -> bool:
        """
        判斷兩張圖片是否相似
        
        Args:
            fingerprint1: 第一個指紋哈希值
            fingerprint2: 第二個指紋哈希值
            threshold: 相似度閾值，漢明距離小於此值被認為是相似圖片
            
        Returns:
            是否為相似圖片
        """
        return ImageFingerprint.is_same_image(fingerprint1, fingerprint2, threshold)
    
    def find_similar_images(self, query_image_path: str, target_paths: list, threshold: int = 5) -> Dict[str, Any]:
        """
        在目標圖片列表中尋找與查詢圖片相似的圖片
        
        Args:
            query_image_path: 查詢圖片路徑
            target_paths: 目標圖片路徑列表
            threshold: 相似度閾值
            
        Returns:
            包含相似圖片結果的字典
        """
        result = {
            'has_similar': False,
            'similar_paths': [],
            'similar_indices': [],
            'distances': [],
            'error': None
        }
        
        try:
            # 計算查詢圖片的哈希值
            query_hash = self.get_image_fingerprint(query_image_path)
            if not query_hash:
                result['error'] = "無法計算查詢圖片的指紋"
                return result
                
            # 檢查每個目標路徑
            for i, path in enumerate(target_paths):
                if not path:
                    continue
                    
                target_hash = self.get_image_fingerprint(path)
                if not target_hash:
                    continue
                    
                distance = self.compare_fingerprints(query_hash, target_hash)
                if distance <= threshold:
                    result['has_similar'] = True
                    result['similar_paths'].append(path)
                    result['similar_indices'].append(i)
                    result['distances'].append(distance)
                    
            return result
                
        except Exception as e:
            result['error'] = str(e)
            logger.exception(f"尋找相似圖片時出錯: {str(e)}")
            return result 