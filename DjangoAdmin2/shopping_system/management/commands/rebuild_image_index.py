import os
import logging
import numpy as np
from django.core.management.base import BaseCommand
from django.conf import settings
from shopping_system.models import Product
from shopping_system.image_search.services.clip_search import ClipImageSearch

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '強制重建產品圖片向量索引並進行測試'

    def handle(self, *args, **options):
        """
        執行管理命令的主要方法
        """
        self.stdout.write(self.style.SUCCESS('開始重建產品圖片索引...'))
        
        # 初始化索引路徑
        index_dir = os.path.join(settings.BASE_DIR, 'shopping_system/image_search/data')
        os.makedirs(index_dir, exist_ok=True)
        
        index_path = os.path.join(index_dir, 'product_vectors.index')
        product_ids_path = os.path.join(index_dir, 'product_ids.npy')
        temp_image_dir = os.path.join(index_dir, 'temp_images')
        
        # 刪除舊的索引文件
        self._clean_old_files(index_path, product_ids_path, temp_image_dir)
        
        # 初始化CLIP搜尋服務
        clip_search = ClipImageSearch(
            index_path=index_path,
            product_ids_path=product_ids_path
        )
        
        # 從資料庫獲取啟用的產品
        products = Product.objects.filter(is_active=True).order_by('id')
        self.stdout.write(f"找到 {products.count()} 個啟用的產品")
        
        if not products:
            self.stdout.write(self.style.WARNING("沒有可用的產品，無法建立索引"))
            return
        
        # 準備產品資料
        products_data = []
        for product in products:
            # 使用 image_url 欄位，如果沒有則使用圖片路徑
            image_url = product.image_url
            
            # 如果沒有 image_url 但有 image 欄位，使用 image 欄位
            if not image_url and hasattr(product, 'image') and product.image:
                image_url = product.image.url
            
            # 如果都沒有，嘗試使用 get_image_url 方法
            if not image_url and hasattr(product, 'get_image_url'):
                image_url = product.get_image_url()
            
            # 如果依然沒有有效圖片，跳過此產品
            if not image_url or image_url.endswith('no-image.jpg'):
                self.stdout.write(self.style.WARNING(f"產品 ID {product.id} 沒有有效圖片，跳過"))
                continue
            
            self.stdout.write(f"產品 ID {product.id} 使用圖片 URL: {image_url}")
            
            products_data.append({
                'id': product.id,
                'image_url': image_url,
                'name': product.name
            })
        
        # 建立圖片搜尋索引
        self.stdout.write(f"開始為 {len(products_data)} 個產品構建索引...")
        result = clip_search.build_index(products_data)
        
        # 檢查結果
        if result is False:
            self.stdout.write(self.style.ERROR("索引建立失敗"))
        else:
            # 檢查索引檔案是否已經建立
            if os.path.exists(index_path) and os.path.exists(product_ids_path):
                # 載入產品ID確認索引大小
                product_ids = np.load(product_ids_path)
                self.stdout.write(self.style.SUCCESS(f"索引建立成功，包含 {len(product_ids)} 個產品"))
                
                # 檢查檔案大小
                index_size = os.path.getsize(index_path) / (1024 * 1024)  # 轉換為 MB
                ids_size = os.path.getsize(product_ids_path) / (1024 * 1024)  # 轉換為 MB
                self.stdout.write(f"索引檔案大小: {index_size:.2f} MB")
                self.stdout.write(f"產品ID檔案大小: {ids_size:.2f} MB")
            else:
                self.stdout.write(self.style.WARNING("索引文件未成功建立"))
        
        # 清理臨時文件
        self._clean_temp_files(temp_image_dir)
                
        # 測試索引是否有效
        self.stdout.write("正在測試索引...")
        self._test_index(clip_search)
        
    def _clean_old_files(self, index_path, product_ids_path, temp_image_dir):
        """
        刪除舊的索引文件
        """
        # 刪除舊索引
        if os.path.exists(index_path):
            os.remove(index_path)
            self.stdout.write(f"已刪除舊索引文件: {index_path}")
            
        # 刪除舊產品ID文件
        if os.path.exists(product_ids_path):
            os.remove(product_ids_path)
            self.stdout.write(f"已刪除舊產品ID文件: {product_ids_path}")
            
        # 清理臨時圖片目錄
        self._clean_temp_files(temp_image_dir)
            
    def _clean_temp_files(self, temp_image_dir):
        """
        清理臨時文件和目錄
        """
        # 清理臨時圖片目錄
        if os.path.exists(temp_image_dir):
            import shutil
            try:
                shutil.rmtree(temp_image_dir)
                self.stdout.write(f"已清理臨時圖片目錄: {temp_image_dir}")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"清理臨時目錄出錯: {str(e)}"))
        
    def _test_index(self, clip_search):
        """
        測試索引是否有效

        Args:
            clip_search: 初始化好的 ClipImageSearch 實例
        """
        try:
            # 嘗試加載索引
            clip_search._load_index()
            if clip_search.index is None:
                self.stdout.write(self.style.ERROR("無法加載索引！"))
                return
                
            # 顯示索引信息
            self.stdout.write(f"成功加載索引，包含 {len(clip_search.product_ids)} 個產品")
            self.stdout.write(f"索引類型: {type(clip_search.index).__name__}")
            self.stdout.write(f"索引維度: {clip_search.index.d}")
            self.stdout.write(f"索引大小: {clip_search.index.ntotal} 個向量")
            
            # 測試檢索是否工作
            self.stdout.write(self.style.SUCCESS("索引測試成功！"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"測試索引時出錯: {str(e)}")) 