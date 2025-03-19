"""
商品模型適配器，用於隔離圖像搜索功能和商品模型的直接依賴
"""
from typing import List, Dict, Any, Optional
from django.db.models import Model
import logging


class ProductAdapter:
    """商品資料適配器，提供標準化接口給圖像搜索功能使用"""

    @staticmethod
    def get_product_by_id(product_id: int, product_model) -> Optional[Dict[str, Any]]:
        """
        根據ID獲取商品資訊
        
        Args:
            product_id: 商品ID
            product_model: 商品模型類
        
        Returns:
            商品資訊字典，若未找到則返回None
        """
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"嘗試獲取商品ID: {product_id}, 類型: {type(product_id)}")
            # 確保product_id是整數
            product_id = int(product_id)
            product = product_model.objects.filter(id=product_id).first()
            
            if not product:
                logger.warning(f"找不到ID為 {product_id} 的商品")
                return None
                
            if not getattr(product, 'is_active', True):
                logger.warning(f"商品ID {product_id} 未啟用")
                return None
                
            result = ProductAdapter.model_to_dict(product)
            logger.info(f"成功獲取商品ID {product_id} 的詳情")
            return result
        except ValueError:
            logger.error(f"無效的商品ID格式: {product_id}, 類型: {type(product_id)}")
            return None
        except product_model.DoesNotExist:
            logger.warning(f"商品ID {product_id} 不存在")
            return None
        except Exception as e:
            logger.exception(f"獲取商品ID {product_id} 時發生未知錯誤: {str(e)}")
            return None

    @staticmethod
    def get_all_active_products(product_model) -> List[Dict[str, Any]]:
        """
        獲取所有啟用的商品
        
        Args:
            product_model: 商品模型類
        
        Returns:
            商品資訊字典列表
        """
        products = product_model.objects.filter(is_active=True)
        return [ProductAdapter.model_to_dict(product) for product in products]

    @staticmethod
    def model_to_dict(product: Model) -> Dict[str, Any]:
        """
        將商品模型轉換為標準字典格式
        
        Args:
            product: 商品模型實例
        
        Returns:
            標準化的商品資訊字典
        """
        result = {
            'id': product.id,
            'name': getattr(product, 'name', ''),
            'price': getattr(product, 'price', 0),
            'is_active': getattr(product, 'is_active', False),
        }
        
        # 可選字段
        if hasattr(product, 'slug'):
            result['slug'] = product.slug
            
        if hasattr(product, 'description'):
            result['description'] = product.description
            
        if hasattr(product, 'discount_price'):
            result['discount_price'] = product.discount_price
            
        # 檢查並處理 image_url 欄位（直接 URL 字段）
        if hasattr(product, 'image_url') and product.image_url:
            result['image_url'] = product.image_url
            result['image'] = product.image_url  # 同時提供 image 欄位以保持兼容性
        # 檢查並處理 image 欄位（文件欄位）
        elif hasattr(product, 'image') and product.image:
            try:
                result['image_url'] = product.image.url
                result['image_path'] = product.image.path
                result['image'] = product.image.url  # 同時提供 image 欄位以保持兼容性
            except (ValueError, AttributeError):
                result['image_url'] = None
                result['image_path'] = None
                result['image'] = None
        # 如果使用 get_image_url 方法
        elif hasattr(product, 'get_image_url') and callable(getattr(product, 'get_image_url')):
            image_url = product.get_image_url()
            result['image_url'] = image_url
            result['image'] = image_url  # 同時提供 image 欄位以保持兼容性
        else:
            result['image_url'] = None
            result['image_path'] = None
            result['image'] = None
            
        # 分類資訊 - 以通用方式嘗試獲取
        category = None
        if hasattr(product, 'category') and product.category:
            category = product.category
        elif hasattr(product, 'product_category') and product.product_category:
            category = product.product_category

        if category:
            result['category'] = {
                'id': getattr(category, 'id', None),
                'name': getattr(category, 'name', '未分類'),
                'slug': getattr(category, 'slug', '')
            }
        else:
            result['category'] = None
            
        return result