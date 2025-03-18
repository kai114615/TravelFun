import os
import logging
import django
import numpy as np
from django.conf import settings

# 設置Django環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoAdmin2.settings')
django.setup()

# 導入必要的模型和服務
from shopping_system.models import Product
from shopping_system.image_search.services.clip_search import ClipImageSearch

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def build_index():
    """
    從資料庫獲取產品資訊並建立圖片搜尋索引
    """
    logger.info("開始建立產品圖片索引...")
    
    # 初始化CLIP搜尋服務
    index_dir = os.path.join(settings.BASE_DIR, 'shopping_system/image_search/data')
    os.makedirs(index_dir, exist_ok=True)
    
    index_path = os.path.join(index_dir, 'product_vectors.index')
    product_ids_path = os.path.join(index_dir, 'product_ids.npy')
    
    clip_search = ClipImageSearch(
        index_path=index_path,
        product_ids_path=product_ids_path
    )
    
    # 從資料庫獲取啟用的產品
    products = Product.objects.filter(is_active=True).order_by('id')
    logger.info(f"找到 {products.count()} 個啟用的產品")
    
    if not products:
        logger.warning("沒有可用的產品，無法建立索引")
        return
    
    # 準備產品資料
    products_data = []
    for product in products:
        # 使用 image_url 欄位，如果沒有則使用圖片路徑
        image_url = product.image_url
        
        # 如果這是外部URL（特別是 momoshop 網站的URL），則跳過
        if image_url and ('momoshop.com.tw' in image_url or 'momo' in image_url):
            logger.warning(f"跳過外部商品圖片: ID {product.id}, URL: {image_url}")
            continue
            
        # 如果沒有 image_url 但有 image 欄位，使用 image 欄位
        if not image_url and hasattr(product, 'image') and product.image:
            image_url = product.image.url
        
        # 如果都沒有，嘗試使用 get_image_url 方法
        if not image_url and hasattr(product, 'get_image_url'):
            image_url = product.get_image_url()
            
        # 如果 get_image_url 返回的是靜態路徑，確保它是完整的URL
        if image_url and image_url.startswith('/static/'):
            from django.contrib.staticfiles.storage import staticfiles_storage
            image_url = staticfiles_storage.url(image_url.replace('/static/', ''))
        
        # 如果依然沒有有效圖片，或者是預設圖片，跳過此產品
        if not image_url or image_url.endswith('no-image.jpg'):
            logger.warning(f"產品 ID {product.id} 沒有有效圖片，跳過")
            continue
        
        logger.info(f"產品 ID {product.id} 使用圖片 URL: {image_url}")
        
        products_data.append({
            'id': product.id,
            'image_url': image_url,
            'name': product.name
        })
    
    # 建立圖片搜尋索引
    logger.info(f"開始為 {len(products_data)} 個產品構建索引...")
    result = clip_search.build_index(products_data)
    
    # 檢查結果
    if result is False:
        logger.error("索引建立失敗")
    else:
        # 檢查索引檔案是否已經建立
        if os.path.exists(index_path) and os.path.exists(product_ids_path):
            # 載入產品ID確認索引大小
            product_ids = np.load(product_ids_path)
            logger.info(f"索引建立成功，包含 {len(product_ids)} 個產品")
        else:
            logger.warning("索引文件未成功建立")

if __name__ == "__main__":
    build_index() 