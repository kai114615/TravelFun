"""
基於CLIP的圖像搜索服務
"""
import os
import certifi
import torch
import numpy as np
import logging
import time
import platform
import faiss
from typing import List, Dict, Any, Optional
from PIL import Image
from django.conf import settings

# 設置 SSL 
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['SSL_CERT_FILE'] = certifi.where()

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ClipImageSearch:
    """基於CLIP模型的圖像搜索服務"""
    
    def __init__(self, index_path=None, product_ids_path=None):
        """
        初始化 CLIP 圖像搜尋服務

        Args:
            index_path: FAISS索引文件路徑，預設為None（使用預設路徑）
            product_ids_path: 產品ID列表文件路徑，預設為None（使用預設路徑）
        """
        # 設置CUDA設備（如果可用）
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        if self.device == 'cpu' and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            # MacOS上使用MPS加速
            self.device = 'mps'
        
        logger.info(f"使用設備: {self.device}")
        
        # 設置模型版本與路徑
        self.model_version = 'ViT-B/32'  # 預設使用 ViT-B/32 模型
        self.model = None
        self.preprocess = None
        
        # 設置索引路徑
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, '../data')
        os.makedirs(data_dir, exist_ok=True)
        
        # 如果提供了自定義路徑，則使用自定義路徑
        self.index_path = index_path if index_path else os.path.join(data_dir, 'product_vectors.index')
        self.product_ids_path = product_ids_path if product_ids_path else os.path.join(data_dir, 'product_ids.npy')
        
        # 設置批量處理大小
        self.batch_size = 16
        
        # 初始化索引和產品ID列表
        self.index = None
        self.product_ids = None

    def _load_clip_model(self):
        """
        載入CLIP模型
        """
        try:
            # 動態導入CLIP，避免在導入時就需要載入模型
            logger.info(f"載入CLIP {self.model_version}模型...")
            import clip
            self.model, self.preprocess = clip.load(self.model_version, device=self.device)
            logger.info("CLIP模型載入完成")
        except Exception as e:
            logger.error(f"載入CLIP模型錯誤: {str(e)}")
            logger.warning("嘗試使用CPU作為後備方案")
            try:
                self.device = "cpu"
                import clip
                self.model, self.preprocess = clip.load(self.model_version, device=self.device)
                logger.info("使用CPU成功載入CLIP模型")
            except Exception as e2:
                logger.error(f"使用CPU載入CLIP模型仍然失敗: {str(e2)}")
                # 設置一個默認值，避免後續代碼出錯
                self.model = None
                self.preprocess = None
                raise RuntimeError(f"無法載入CLIP模型: {str(e2)}")
    
    def _load_index(self):
        """
        按需載入FAISS索引
        """
        if self.index is not None and self.product_ids is not None:
            return
            
        # 加載CLIP模型（向量化需要）
        self._load_clip_model()
        
        # 檢查索引文件是否存在
        if not os.path.exists(self.index_path) or not os.path.exists(self.product_ids_path):
            logger.warning(f"索引文件不存在: {self.index_path} 或 {self.product_ids_path}")
            # 初始化空索引
            import faiss
            self.index = faiss.IndexFlatIP(512)  # CLIP ViT-B/32 輸出 512 維度向量
            self.product_ids = np.array([], dtype=np.int64)
            return
            
        try:
            # 載入索引
            import faiss
            self.index = faiss.read_index(self.index_path)
            self.product_ids = np.load(self.product_ids_path)
            
            # 確保產品ID是正確的數據類型
            self.product_ids = self.product_ids.astype(np.int64)
            
            logger.info(f"成功載入索引，包含 {len(self.product_ids)} 個產品向量")
        except Exception as e:
            logger.exception(f"載入索引時出錯: {str(e)}")
            # 初始化空索引
            self.index = faiss.IndexFlatIP(512)
            self.product_ids = np.array([], dtype=np.int64)
    
    def _save_index(self):
        """
        保存索引和產品ID到文件
        """
        if self.index is None or self.product_ids is None:
            logger.error("無法保存索引：索引或產品ID為空")
            return False
            
        try:
            # 確保目錄存在
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            # 保存索引
            import faiss
            faiss.write_index(self.index, self.index_path)
            
            # 保存產品ID
            np.save(self.product_ids_path, self.product_ids)
            
            logger.info(f"成功保存索引，包含 {len(self.product_ids)} 個產品向量")
            return True
        except Exception as e:
            logger.exception(f"保存索引時出錯: {str(e)}")
            return False
            
    def _get_image_vector_from_url(self, image_url: str) -> Optional[np.ndarray]:
        """
        從URL獲取圖片並生成向量
        
        Args:
            image_url: 圖片URL
            
        Returns:
            圖片向量，如果獲取失敗則返回None
        """
        if not image_url:
            return None
            
        # 加載CLIP模型
        self._load_clip_model()
        
        try:
            # 從URL獲取圖片
            if image_url.startswith(('http://', 'https://')):
                import requests
                from io import BytesIO
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Referer': 'https://www.momoshop.com.tw/',
                    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                }
                
                response = requests.get(image_url, timeout=10, headers=headers)
                if response.status_code != 200:
                    logger.error(f"下載圖片失敗: {image_url}, 狀態碼: {response.status_code}")
                    return None
                    
                img = Image.open(BytesIO(response.content)).convert("RGB")
            else:
                # 本地文件路徑
                img = Image.open(image_url).convert("RGB")
                
            # 預處理圖片
            processed_image = self.preprocess(img).unsqueeze(0).to(self.device)
            
            # 生成特徵向量
            with torch.no_grad():
                image_features = self.model.encode_image(processed_image)
                
            # 正規化特徵向量
            image_features /= image_features.norm(dim=-1, keepdim=True)
            
            # 轉換為numpy陣列
            vector = image_features.cpu().numpy().astype('float32')
            
            return vector
            
        except Exception as e:
            logger.exception(f"生成圖片向量時出錯: {str(e)}")
            return None

    def build_index(self, products: List[Dict[str, Any]]):
        """
        為產品列表構建向量索引

        Args:
            products: 產品列表，每個產品必須有id和image_url欄位
            
        Returns:
            建立成功返回 True，失敗返回 False
        """
        start_time = time.time()
        self._load_clip_model()

        if not products:
            logger.warning("沒有產品數據，無法建立索引")
            return False

        # 確保索引目錄存在
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        # 創建臨時圖片目錄
        temp_image_dir = os.path.join(os.path.dirname(self.index_path), 'temp_images')
        os.makedirs(temp_image_dir, exist_ok=True)

        # 初始化向量列表和ID列表
        vectors = []
        product_ids = []
        total_products = len(products)
        processed_count = 0

        try:
            # 批量處理圖片，每批最多32張
            batch_size = min(self.batch_size, 32)
            for i in range(0, total_products, batch_size):
                batch_products = products[i:i + batch_size]
                batch_images = []
                batch_valid_indices = []

                for idx, product in enumerate(batch_products):
                    image_url = product.get('image_url')
                    product_id = product.get('id')

                    if not image_url or not product_id:
                        logger.warning(f"產品缺少必要欄位: {product}")
                        continue

                    # 創建唯一的臨時文件名
                    temp_image_path = os.path.join(temp_image_dir, f"{product_id}.jpg")

                    try:
                        # 下載圖片
                        if image_url.startswith(('http://', 'https://')):
                            # 從網絡下載圖片
                            logger.info(f"從網絡下載圖片: {image_url}")
                            try:
                                import requests
                                response = requests.get(image_url, timeout=30)
                                if response.status_code == 200:
                                    with open(temp_image_path, 'wb') as f:
                                        f.write(response.content)
                                    logger.info(f"成功下載圖片: {image_url}")
                                else:
                                    logger.warning(f"下載圖片失敗: {image_url}, 狀態碼: {response.status_code}")
                                    continue
                            except Exception as download_error:
                                logger.exception(f"下載圖片時出錯: {str(download_error)}")
                                continue
                        else:
                            # 本地圖片，可能是相對路徑
                            if image_url.startswith('/'):
                                # 絕對路徑
                                local_path = image_url
                            else:
                                # 相對路徑，加上 MEDIA_ROOT
                                from django.conf import settings
                                local_path = os.path.join(settings.MEDIA_ROOT, image_url)

                            # 複製到臨時目錄
                            if os.path.exists(local_path):
                                import shutil
                                shutil.copy2(local_path, temp_image_path)
                                logger.info(f"使用本地圖片: {local_path}")
                            else:
                                logger.warning(f"本地圖片不存在: {local_path}")
                                continue

                        # 加載和預處理圖片
                        img = Image.open(temp_image_path).convert("RGB")
                        processed_image = self.preprocess(img)
                        batch_images.append(processed_image)
                        batch_valid_indices.append(idx)
                        processed_count += 1
                        logger.info(f"成功處理產品 {product_id} 的圖片")

                    except Exception as e:
                        logger.exception(f"處理產品 {product_id} 的圖片時出錯: {str(e)}")

                # 如果批次中有有效圖片
                if batch_images:
                    # 將批次圖片轉換為張量
                    batch_tensor = torch.stack(batch_images).to(self.device)

                    # 用CLIP模型生成特徵向量
                    with torch.no_grad():
                        batch_features = self.model.encode_image(batch_tensor)

                    # 正規化特徵向量
                    batch_features /= batch_features.norm(dim=-1, keepdim=True)

                    # 將特徵向量轉換為NumPy數組
                    batch_features_np = batch_features.cpu().numpy().astype('float32')

                    # 為有效索引添加向量和ID
                    for j, idx in enumerate(batch_valid_indices):
                        vectors.append(batch_features_np[j])
                        product_ids.append(batch_products[idx]['id'])

                    logger.info(f"處理了批次 {i//batch_size + 1}/{total_products//batch_size + 1}")

            # 如果沒有有效向量
            if not vectors:
                logger.warning("沒有成功處理任何產品圖片，無法建立索引")
                return False

            # 創建FAISS索引
            vectors_np = np.array(vectors).astype('float32')
            product_ids_np = np.array(product_ids)

            dimension = vectors_np.shape[1]
            index = faiss.IndexFlatIP(dimension)
            index.add(vectors_np)

            # 保存索引和產品ID
            logger.info(f"正在保存索引到 {self.index_path}...")
            faiss.write_index(index, self.index_path)
            logger.info(f"正在保存產品ID到 {self.product_ids_path}...")
            np.save(self.product_ids_path, product_ids_np)

            # 更新實例變量
            self.index = index
            self.product_ids = product_ids_np

            elapsed_time = time.time() - start_time
            logger.info(f"索引建立完成，包含 {len(product_ids)} 個產品，耗時 {elapsed_time:.2f} 秒")
            
            # 顯示索引文件大小
            index_size = os.path.getsize(self.index_path) / (1024 * 1024)  # 轉換為 MB
            ids_size = os.path.getsize(self.product_ids_path) / (1024 * 1024)  # 轉換為 MB
            logger.info(f"索引檔案大小: {index_size:.2f} MB")
            logger.info(f"產品ID檔案大小: {ids_size:.2f} MB")
            
            return True
            
        except Exception as e:
            logger.exception(f"建立索引時發生錯誤: {str(e)}")
            return False
            
        finally:
            # 清理臨時圖片目錄
            logger.info("清理臨時文件...")
            for file in os.listdir(temp_image_dir):
                try:
                    os.remove(os.path.join(temp_image_dir, file))
                except Exception as e:
                    logger.warning(f"刪除臨時文件時出錯: {str(e)}")
            
            try:
                os.rmdir(temp_image_dir)
                logger.info(f"已刪除臨時目錄: {temp_image_dir}")
            except Exception as e:
                logger.warning(f"刪除臨時目錄時出錯: {str(e)}")

    def search_by_image(self, image_path: str, top_k: int = 5, threshold: float = 0.2) -> List[Dict[str, any]]:
        """
        使用圖片搜尋相似商品

        Args:
            image_path: 查詢圖片路徑
            top_k: 返回結果數量
            threshold: 相似度閾值 (0-1)，低於此值的結果將被過濾

        Returns:
            包含產品ID、相似度分數和排名的結果列表
        """
        # 加載CLIP模型
        self._load_clip_model()
        # 加載索引
        self._load_index()
        
        if self.index is None:
            logger.error("索引尚未建立，無法搜尋")
            return []
            
        # 判斷圖片是否為URL或本地路徑
        try:
            if image_path.startswith(('http://', 'https://')):
                logger.info(f"從網路載入圖片: {image_path}")
                import requests
                from io import BytesIO
                
                response = requests.get(image_path, timeout=10)
                if response.status_code != 200:
                    logger.error(f"無法下載圖片: {image_path}, 狀態碼: {response.status_code}")
                    return []
                    
                img = Image.open(BytesIO(response.content)).convert("RGB")
            else:
                logger.info(f"從本地載入圖片: {image_path}")
                img = Image.open(image_path).convert("RGB")
                
            # 預處理圖片
            processed_image = self.preprocess(img).unsqueeze(0).to(self.device)
            
            # 生成特徵向量
            with torch.no_grad():
                image_features = self.model.encode_image(processed_image)
                
            # 正規化特徵向量
            image_features /= image_features.norm(dim=-1, keepdim=True)
            
            # 轉換為numpy陣列
            query_vector = image_features.cpu().numpy().astype('float32')
            
            # 在索引中搜索相似向量
            scores, indices = self.index.search(query_vector, min(top_k * 2, len(self.product_ids)))
            
            # 整理搜尋結果
            results = []
            filtered_count = 0
            
            # 解壓縮結果
            scores = scores[0]  # shape (1, top_k) -> (top_k,)
            indices = indices[0]  # shape (1, top_k) -> (top_k,)
            
            for rank, (score, idx) in enumerate(zip(scores, indices)):
                # 內積相似度現在範圍是[-1, 1]，將其映射到[0, 1]
                normalized_score = float((score + 1) / 2.0)
                
                # 過濾低於閾值的結果
                if normalized_score < threshold:
                    filtered_count += 1
                    continue
                    
                # 獲取產品ID
                if 0 <= idx < len(self.product_ids):
                    product_id = int(self.product_ids[idx])
                    
                    results.append({
                        'product_id': product_id,
                        'score': normalized_score,
                        'rank': rank + 1  # 排名從1開始
                    })
                    
                    # 如果我們已經有了足夠的結果，可以提前退出
                    if len(results) >= top_k:
                        break
                        
            # 按相似度降序排序
            results.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"搜尋完成: 找到 {len(results)} 個結果，過濾了 {filtered_count} 個低相似度結果")
            return results
            
        except Exception as e:
            logger.exception(f"圖片搜尋過程中發生錯誤: {str(e)}")
            return []

    def update_product_in_index(self, product: Dict[str, Any]):
        """
        更新單個產品在索引中的向量
        
        Args:
            product: 包含商品資訊的字典，必須包含 id 和 image_url
        
        Returns:
            更新是否成功
        """
        # 檢查參數
        if 'id' not in product or 'image_url' not in product:
            logger.error("更新索引需要提供產品ID和圖片URL")
            return False
            
        product_id = product['id']
        image_url = product['image_url']
        
        # 檢查圖片URL
        if not image_url or image_url.endswith('no-image.jpg'):
            logger.warning(f"產品 {product_id} 沒有有效的圖片URL")
            return False
            
        # 載入模型和索引
        self._load_clip_model()
        self._load_index()
        
        if self.index is None:
            logger.error("索引尚未建立，無法更新")
            return False
            
        try:
            # 檢查產品是否已在索引中
            if self.product_ids is not None:
                product_idx = np.where(self.product_ids == product_id)[0]
                
                # 獲取圖片向量
                vector = self._get_image_vector_from_url(image_url)
                if vector is None:
                    logger.error(f"無法獲取產品 {product_id} 的圖片向量")
                    return False
                    
                # 如果產品已在索引中，更新其向量
                if len(product_idx) > 0:
                    idx = product_idx[0]
                    # 更新向量 (對於基於 FAISS 的索引可能需要特定實現)
                    logger.info(f"產品 {product_id} 已在索引中，更新其向量")
                    # TODO: 實現更新向量的邏輯
                    return True
                else:
                    # 如果產品不在索引中，添加到索引
                    logger.info(f"產品 {product_id} 不在索引中，添加到索引")
                    # 添加到索引
                    self.index.add(vector)
                    # 更新產品ID列表
                    self.product_ids = np.append(self.product_ids, product_id)
                    # 保存索引和產品ID
                    self._save_index()
                    return True
            else:
                logger.error("產品ID列表尚未載入，無法更新")
                return False
                
        except Exception as e:
            logger.exception(f"更新產品 {product_id} 在索引中的向量時出錯: {str(e)}")
            return False
            
    def remove_product_from_index(self, product_id: int) -> bool:
        """
        從索引中移除指定產品
        
        Args:
            product_id: 要移除的產品ID
            
        Returns:
            是否成功移除
        """
        # 載入索引
        self._load_index()
        
        if self.index is None or self.product_ids is None:
            logger.error("索引尚未建立，無法移除產品")
            return False
            
        try:
            # 檢查產品是否在索引中
            product_idx = np.where(self.product_ids == product_id)[0]
            
            if len(product_idx) == 0:
                logger.warning(f"產品ID {product_id} 不在索引中")
                return False
                
            idx = product_idx[0]
            logger.info(f"將產品ID {product_id} (索引位置 {idx}) 從索引中移除")
            
            # 創建新的產品ID數組，排除要移除的ID
            new_product_ids = np.delete(self.product_ids, idx)
            
            # 對於FAISS索引，我們無法直接移除一個向量
            # 因此，重新創建一個索引，並添加除了要移除的向量外的所有向量
            import faiss
            d = self.index.d  # 獲取向量維度
            new_index = faiss.IndexFlatIP(d)  # 創建一個新的內積索引
            
            # 獲取所有向量
            all_vectors = np.zeros((len(self.product_ids), d), dtype=np.float32)
            for i in range(len(self.product_ids)):
                all_vectors[i] = self.index.reconstruct(i)
                
            # 創建不包含要移除的向量的新數組
            new_vectors = np.delete(all_vectors, idx, axis=0)
            
            # 添加向量到新索引
            if len(new_vectors) > 0:
                new_index.add(new_vectors)
                
            # 保存新索引和產品ID
            self.index = new_index
            self.product_ids = new_product_ids
            self._save_index()
            
            logger.info(f"成功從索引中移除產品ID {product_id}")
            return True
            
        except Exception as e:
            logger.exception(f"從索引中移除產品ID {product_id} 時出錯: {str(e)}")
            return False


# 單例模式
_clip_search_instance = None

def get_clip_search():
    """
    獲取ClipImageSearch實例 (單例模式)
    """
    global _clip_search_instance
    if _clip_search_instance is None:
        _clip_search_instance = ClipImageSearch()
    return _clip_search_instance