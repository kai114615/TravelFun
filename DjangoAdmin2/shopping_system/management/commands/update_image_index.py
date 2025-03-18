import os
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from shopping_system.models import Product
from shopping_system.image_search.services.clip_search import ClipImageSearch

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '更新單個產品的圖片向量索引'
    
    def add_arguments(self, parser):
        parser.add_argument('--product_id', type=int, help='要更新的產品ID')
    
    def handle(self, *args, **options):
        """
        執行管理命令的主要方法
        """
        product_id = options.get('product_id')
        if not product_id:
            self.stdout.write(self.style.ERROR('請提供要更新的產品ID'))
            return
            
        self.stdout.write(self.style.SUCCESS(f'開始更新產品ID {product_id} 的圖片索引...'))
        
        # 檢查產品是否存在
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'產品ID {product_id} 不存在'))
            return
            
        # 如果產品不活躍，建議從索引中移除
        if not product.is_active:
            self.stdout.write(self.style.WARNING(f'產品ID {product_id} 不活躍，應該從索引中移除'))
            return
        
        # 初始化索引路徑
        index_dir = os.path.join(settings.BASE_DIR, 'shopping_system/image_search/data')
        os.makedirs(index_dir, exist_ok=True)
        
        index_path = os.path.join(index_dir, 'product_vectors.index')
        product_ids_path = os.path.join(index_dir, 'product_ids.npy')
        
        # 檢查索引文件是否存在
        if not os.path.exists(index_path) or not os.path.exists(product_ids_path):
            self.stdout.write(self.style.WARNING('索引文件不存在，請先執行 rebuild_image_index 命令'))
            return
            
        # 初始化CLIP搜尋服務
        clip_search = ClipImageSearch(
            index_path=index_path,
            product_ids_path=product_ids_path
        )
        
        # 獲取產品圖片URL
        image_url = product.image_url
        if not image_url:
            self.stdout.write(self.style.WARNING(f'產品ID {product_id} 沒有圖片URL'))
            return
        
        # 更新產品在索引中的向量
        try:
            result = clip_search.update_product_in_index({
                'id': product.id,
                'image_url': image_url
            })
            
            if result:
                self.stdout.write(self.style.SUCCESS(f'成功更新產品ID {product_id} 的圖片索引'))
            else:
                self.stdout.write(self.style.ERROR(f'更新產品ID {product_id} 的圖片索引失敗'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'更新產品ID {product_id} 的圖片索引時出錯: {str(e)}')) 