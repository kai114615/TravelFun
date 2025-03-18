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
import clip  # 直接導入 clip 庫

from shopping_system.models import Product

class Command(BaseCommand):
    help = '建立產品圖片向量索引用於圖片搜索'

    def handle(self, *args, **options):
        # 強制使用 CPU 設備，避免 MPS 的兼容性問題
        device = "cpu"
        self.stdout.write(f"使用設備: {device}")
        
        try:
            # 直接載入 CLIP 模型
            self.stdout.write("🔄 正在載入 CLIP 模型...")
            model, preprocess = clip.load("ViT-B/32", device=device)
            self.stdout.write("✅ CLIP 模型載入完成")
            
            # 設置 FAISS 索引保存路徑
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(current_dir, 'image_search', 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            index_path = os.path.join(data_dir, 'product_vectors.index')
            product_ids_path = os.path.join(data_dir, 'product_ids.npy')
            
            self.stdout.write(f"索引將保存至: {index_path}")
            self.stdout.write(f"產品 ID 將保存至: {product_ids_path}")
            
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
            
            # 批次處理，每批最多處理 32 個產品
            batch_size = 32
            batches = (product_count + batch_size - 1) // batch_size
            
            self.stdout.write("🔄 開始處理產品圖片...")
            for batch_idx in range(batches):
                start_idx = batch_idx * batch_size
                end_idx = min((batch_idx + 1) * batch_size, product_count)
                
                batch_products = products[start_idx:end_idx]
                batch_images = []
                batch_valid_indices = []
                batch_products_to_use = []
                
                for i, product in enumerate(batch_products):
                    # 使用 image_url 而不是 image
                    if not product.image_url:
                        self.stdout.write(f"警告: 產品 {product.id} ({product.name}) 沒有圖片URL")
                        continue
                        
                    try:
                        # 從網絡下載圖片
                        response = requests.get(product.image_url, timeout=10)
                        if response.status_code != 200:
                            self.stdout.write(self.style.WARNING(f"下載圖片失敗 (產品 {product.id}): HTTP狀態碼 {response.status_code}"))
                            continue
                            
                        # 載入並預處理圖片
                        try:
                            img = Image.open(BytesIO(response.content)).convert('RGB')
                            batch_images.append(preprocess(img))
                            batch_valid_indices.append(i)
                            batch_products_to_use.append(product)
                            self.stdout.write(f"成功載入圖片: {product.image_url}")
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f"圖片處理錯誤 (產品 {product.id}): {e}"))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"獲取圖片錯誤 (產品 {product.id}): {e}"))
                
                if not batch_images:
                    self.stdout.write(f"批次 {batch_idx+1}/{batches} 中沒有有效圖片")
                    continue
                    
                # 合併批次圖片並轉換為張量
                batch_tensor = torch.stack(batch_images).to(device)
                
                # 使用 CLIP 模型獲取特徵向量
                with torch.no_grad():
                    batch_features = model.encode_image(batch_tensor)
                    
                # 正規化特徵向量
                batch_features /= batch_features.norm(dim=-1, keepdim=True)
                
                # 將特徵向量轉換為 NumPy 陣列並添加到向量列表
                batch_features_np = batch_features.cpu().numpy().astype('float32')
                
                # 添加產品ID和向量
                for i, product in enumerate(batch_products_to_use):
                    product_ids.append(product.id)
                    vectors.append(batch_features_np[i])
                
                self.stdout.write(f"完成批次 {batch_idx+1}/{batches} 處理")
            
            # 確保我們有有效的向量
            if not vectors:
                self.stdout.write(self.style.ERROR("沒有找到有效的產品圖片，無法建立索引"))
                return
            
            # 將向量列表轉換為 NumPy 陣列
            vectors_np = np.array(vectors).astype('float32')
            product_ids_np = np.array(product_ids)
            
            # 建立 FAISS 索引
            self.stdout.write("🔄 建立 FAISS 索引...")
            dimension = vectors_np.shape[1]
            index = faiss.IndexFlatIP(dimension)
            index.add(vectors_np)
            
            # 保存索引和產品 ID
            self.stdout.write(f"保存索引到 {index_path}")
            faiss.write_index(index, index_path)
            
            self.stdout.write(f"保存產品 ID 到 {product_ids_path}")
            np.save(product_ids_path, product_ids_np)
            
            self.stdout.write(self.style.SUCCESS(f"✅ 索引建立完成! 共處理 {len(product_ids)} 個產品"))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"建立索引時發生錯誤: {e}"))
            import traceback
            self.stdout.write(traceback.format_exc()) 