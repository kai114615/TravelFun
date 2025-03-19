import os
import sys
import numpy as np
import torch
import faiss
from PIL import Image
import requests
from io import BytesIO
from django.core.management.base import BaseCommand
from tqdm import tqdm
import traceback
import logging
from django.conf import settings

from shopping_system.models import Product

# 設置日誌格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '建立產品圖片向量索引用於圖片搜索'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='強制重新構建索引，即使已存在'
        )
        parser.add_argument(
            '--device',
            type=str,
            default='cpu',
            help='使用的設備 (cpu, cuda, mps)'
        )
    
    def handle(self, *args, **options):
        force_rebuild = options['force']
        device = options.get('device', 'cpu')
        
        # 檢查設備可用性
        if device == 'cuda' and not torch.cuda.is_available():
            self.stdout.write(self.style.WARNING("CUDA不可用，將使用CPU"))
            device = 'cpu'
        elif device == 'mps' and (not hasattr(torch.backends, 'mps') or not torch.backends.mps.is_available()):
            self.stdout.write(self.style.WARNING("MPS不可用，將使用CPU"))
            device = 'cpu'
        
        self.stdout.write(f"使用設備: {device}")
        
        try:
            # 導入CLIP (延遲導入以處理可能的導入錯誤)
            try:
                import clip
                self.stdout.write("✅ 成功導入CLIP庫")
            except ImportError as e:
                self.stdout.write(self.style.ERROR(f"無法導入CLIP庫: {e}"))
                self.stdout.write(self.style.ERROR("請安裝必要的依賴: pip install -r requirements.clip.windows.txt"))
                return
            
            # 設置索引文件路徑
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(current_dir, 'image_search', 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            index_path = os.path.join(data_dir, 'product_vectors.index')
            product_ids_path = os.path.join(data_dir, 'product_ids.npy')
            
            # 檢查索引是否已存在
            if os.path.exists(index_path) and os.path.exists(product_ids_path) and not force_rebuild:
                self.stdout.write(self.style.WARNING("索引文件已存在，使用 --force 參數強制重新構建"))
                return
            
            # 載入CLIP模型
            try:
                self.stdout.write("🔄 正在載入 CLIP 模型...")
                model, preprocess = clip.load("ViT-B/32", device=device)
                self.stdout.write("✅ CLIP 模型載入完成")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"載入CLIP模型失敗: {e}"))
                self.stdout.write(traceback.format_exc())
                return
            
            # 獲取所有活躍產品
            products = Product.objects.filter(is_active=True)
            product_count = products.count()
            self.stdout.write(f"找到 {product_count} 個活躍產品")
            
            if product_count == 0:
                self.stdout.write(self.style.ERROR("沒有找到活躍產品，無法建立索引"))
                return
            
            # 初始化向量和ID列表
            product_ids = []
            vectors = []
            
            # 處理每個產品圖片
            self.stdout.write("🔄 開始處理產品圖片...")
            with torch.no_grad():
                for product in tqdm(products, desc="處理產品圖片"):
                    try:
                        # 獲取圖片URL
                        image_url = product.image_url  # 假設有這個欄位
                        
                        # 跳過沒有圖片的產品
                        if not image_url:
                            self.stdout.write(f"跳過產品 {product.id}: 沒有圖片")
                            continue
                        
                        # 下載圖片
                        try:
                            response = requests.get(image_url, timeout=10)
                            if response.status_code != 200:
                                self.stdout.write(f"跳過產品 {product.id}: 下載圖片失敗，狀態碼 {response.status_code}")
                                continue
                                
                            image_data = BytesIO(response.content)
                            image = Image.open(image_data).convert('RGB')
                        except Exception as img_err:
                            self.stdout.write(f"跳過產品 {product.id}: 圖片處理錯誤 {str(img_err)}")
                            continue
                        
                        # 使用CLIP處理圖片
                        processed_image = preprocess(image).unsqueeze(0).to(device)
                        image_features = model.encode_image(processed_image)
                        image_features /= image_features.norm(dim=-1, keepdim=True)
                        
                        # 添加到向量列表
                        vectors.append(image_features.cpu().numpy().astype(np.float32).flatten())
                        product_ids.append(product.id)
                        
                    except Exception as e:
                        self.stdout.write(f"處理產品 {product.id} 時出錯: {str(e)}")
                        continue
            
            # 檢查是否有處理成功的產品
            if len(vectors) == 0:
                self.stdout.write(self.style.ERROR("沒有成功處理任何產品圖片，無法創建索引"))
                return
                
            # 轉換為numpy數組
            vectors_array = np.array(vectors).astype(np.float32)
            product_ids_array = np.array(product_ids, dtype=np.int64)
            
            self.stdout.write(f"成功處理 {len(vectors)} 個產品圖片")
            self.stdout.write(f"向量形狀: {vectors_array.shape}")
            
            # 建立FAISS索引
            self.stdout.write("🔄 建立FAISS索引...")
            index = faiss.IndexFlatIP(vectors_array.shape[1])  # 內積相似度（餘弦相似度）
            index.add(vectors_array)
            
            # 保存索引和產品ID
            self.stdout.write(f"🔄 保存索引到 {index_path}")
            faiss.write_index(index, index_path)
            
            self.stdout.write(f"🔄 保存產品ID到 {product_ids_path}")
            np.save(product_ids_path, product_ids_array)
            
            self.stdout.write(self.style.SUCCESS(f"✅ 成功建立索引，包含 {len(product_ids)} 個產品"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"建立索引時發生錯誤: {str(e)}"))
            self.stdout.write(traceback.format_exc()) 