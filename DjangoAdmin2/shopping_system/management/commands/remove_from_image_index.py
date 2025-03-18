import os
import logging
import numpy as np
from django.core.management.base import BaseCommand
from django.conf import settings
from shopping_system.image_search.services.clip_search import ClipImageSearch

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '從圖片向量索引中移除指定產品'
    
    def add_arguments(self, parser):
        parser.add_argument('--product_id', type=int, help='要移除的產品ID')
    
    def handle(self, *args, **options):
        """
        執行管理命令的主要方法
        """
        product_id = options.get('product_id')
        if not product_id:
            self.stdout.write(self.style.ERROR('請提供要移除的產品ID'))
            return
            
        self.stdout.write(self.style.SUCCESS(f'開始從圖片索引中移除產品ID {product_id}...'))
        
        # 初始化索引路徑
        index_dir = os.path.join(settings.BASE_DIR, 'shopping_system/image_search/data')
        index_path = os.path.join(index_dir, 'product_vectors.index')
        product_ids_path = os.path.join(index_dir, 'product_ids.npy')
        
        # 檢查索引文件是否存在
        if not os.path.exists(index_path) or not os.path.exists(product_ids_path):
            self.stdout.write(self.style.WARNING('索引文件不存在，無需移除'))
            return
            
        try:
            # 載入產品ID
            product_ids = np.load(product_ids_path)
            
            # 檢查產品ID是否在索引中
            if product_id not in product_ids:
                self.stdout.write(self.style.WARNING(f'產品ID {product_id} 不在索引中'))
                return
                
            # 初始化CLIP搜尋服務
            clip_search = ClipImageSearch(
                index_path=index_path,
                product_ids_path=product_ids_path
            )
            
            # 從索引中移除產品
            result = clip_search.remove_product_from_index(product_id)
            
            if result:
                self.stdout.write(self.style.SUCCESS(f'成功從圖片索引中移除產品ID {product_id}'))
            else:
                self.stdout.write(self.style.ERROR(f'從圖片索引中移除產品ID {product_id} 失敗'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'從圖片索引中移除產品ID {product_id} 時出錯: {str(e)}')) 