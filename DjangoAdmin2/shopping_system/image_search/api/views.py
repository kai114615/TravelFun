"""
圖像搜索API視圖
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import os
import tempfile
from django.conf import settings
import logging

from ..services.clip_search import get_clip_search
from ..adapters.product_adapter import ProductAdapter

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class ImageSearchAPIView(APIView):
    """處理圖片搜索的API視圖"""
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [AllowAny]  # 允許任何用戶訪問，包括匿名用戶
    authentication_classes = []  # 不要求任何認證

    def post(self, request, *args, **kwargs):
        """接收上傳圖片並返回相似商品"""
        try:
            logger.info("接收到圖像搜索請求")
            logger.info(f"請求方法: {request.method}")
            logger.info(f"請求標頭: {request.headers}")
            logger.info(f"請求內容類型: {request.content_type}")
            logger.info(f"請求內容: {request.data}")
            logger.info(f"FILES內容: {request.FILES}")
            logger.info(f"COOKIES: {request.COOKIES}")
            logger.info(f"META: {request.META}")
            
            image_file = request.FILES.get('image')
            if not image_file:
                logger.warning("未提供圖片文件")
                return Response({"error": "請上傳圖片", "success": False}, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"上傳的圖片: {image_file.name}, 大小: {image_file.size} bytes")
            
            # 將上傳的圖片保存到臨時文件
            temp_file = None
            temp_path = None
            
            # 記錄正在使用AllowAny權限
            logger.info(f"使用的權限類: {self.permission_classes}")
            logger.info(f"使用的認證類: {self.authentication_classes}")
        
            try:
                # 創建臨時文件
                fd, temp_path = tempfile.mkstemp(suffix='.jpg')
                os.close(fd)
                
                # 保存上傳的圖片到臨時文件
                with open(temp_path, 'wb') as f:
                    for chunk in image_file.chunks():
                        f.write(chunk)
                
                logger.info(f"已保存圖片到臨時文件: {temp_path}")
                
                # 使用CLIP搜索相似產品
                clip_search = get_clip_search()
                logger.info("已初始化CLIP搜索")
                
                similar_ids = clip_search.search_by_image(temp_path, top_k=10)
                logger.info(f"搜索完成，找到相似的產品IDs: {similar_ids}")
                
                # 使用產品適配器獲取詳細信息
                product_adapter = ProductAdapter()
                products = []
                for product_id in similar_ids:
                    product = product_adapter.get_product_by_id(product_id)
                    if product:  # 可能有些產品ID已不存在
                        products.append(product)
                
                logger.info(f"返回產品數量: {len(products)}")
                
                return Response({
                    "success": True,
                    "products": products
                })
            except Exception as e:
                logger.exception(f"處理圖片時發生異常: {str(e)}")
                return Response(
                    {"error": f"處理圖片時出錯: {str(e)}", "success": False},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            finally:
                # 確保臨時文件被刪除
                if temp_path and os.path.exists(temp_path):
                    os.unlink(temp_path)
                    logger.info(f"已刪除臨時文件: {temp_path}")
        except Exception as outer_e:
            logger.exception(f"API視圖外層異常: {str(outer_e)}")
            return Response(
                {"error": f"處理請求時出錯: {str(outer_e)}", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )