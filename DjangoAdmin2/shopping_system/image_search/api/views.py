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
import traceback
from django.conf import settings
import logging
import numpy as np

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
                
                # 檢查臨時文件是否存在
                if not os.path.exists(temp_path):
                    logger.error(f"臨時文件未能成功創建: {temp_path}")
                    return Response(
                        {"error": "圖片保存失敗", "success": False},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                # 檢查文件大小
                file_size = os.path.getsize(temp_path)
                logger.info(f"臨時文件大小: {file_size} bytes")
                if file_size == 0:
                    logger.error("臨時文件大小為0字節")
                    return Response(
                        {"error": "保存的圖片為空", "success": False},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                # 使用CLIP搜索相似產品
                try:
                    clip_search = get_clip_search()
                    logger.info("已初始化CLIP搜索")
                    
                    # 檢查索引是否已加載
                    if not clip_search.is_index_loaded():
                        logger.error("CLIP索引未加載，需要先構建索引")
                        return Response(
                            {"error": "搜索索引未初始化，請聯繫管理員", "success": False},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
                    
                    similar_ids = clip_search.search_by_image(temp_path, top_k=10)
                    logger.info(f"搜索完成，找到相似的產品IDs: {similar_ids}")
                    
                    # 檢查是否有搜索結果
                    if not similar_ids:
                        logger.warning("未找到任何相似產品")
                        return Response({
                            "success": True,
                            "products": [],
                            "message": "未找到相似產品",
                            "debug_info": {
                                "index_path": clip_search.index_path,
                                "product_ids_path": clip_search.product_ids_path,
                                "index_size": clip_search.index.ntotal if clip_search.index else 0,
                                "product_ids_count": len(clip_search.product_ids) if clip_search.product_ids is not None else 0
                            }
                        })
                    
                    # 從搜索結果中提取產品ID
                    product_ids = [item['product_id'] for item in similar_ids]
                    logger.info(f"提取的純產品ID列表: {product_ids}")
                    
                    # 使用產品適配器獲取詳細信息
                    product_adapter = ProductAdapter()
                    products = []
                    
                    # 導入商品模型類
                    from shopping_system.models import Product
                    
                    # 檢查產品數量
                    product_count = Product.objects.filter(is_active=True).count()
                    logger.info(f"資料庫中有 {product_count} 個活躍產品")
                    
                    for product_id in product_ids:
                        try:
                            # 確保產品ID是整數
                            if isinstance(product_id, np.integer):
                                product_id = int(product_id)
                            logger.info(f"處理商品ID: {product_id}, 類型: {type(product_id)}")
                            
                            product = product_adapter.get_product_by_id(product_id, Product)
                            if product:  # 可能有些產品ID已不存在
                                products.append(product)
                            else:
                                logger.warning(f"找不到產品ID: {product_id}")
                        except Exception as prod_error:
                            logger.exception(f"獲取產品ID {product_id} 信息時出錯: {str(prod_error)}")
                            # 繼續處理其他產品，不中斷整個流程
                    
                    logger.info(f"返回產品數量: {len(products)}")
                    
                    # 如果沒有找到產品
                    if not products:
                        return Response({
                            "success": True,
                            "products": [],
                            "message": "找到相似商品ID，但無法獲取商品詳情",
                            "debug_info": {
                                "similar_ids": [item['product_id'] for item in similar_ids],
                                "product_count": product_count
                            }
                        })
                    
                    return Response({
                        "success": True,
                        "products": products
                    })
                except Exception as clip_error:
                    logger.exception(f"CLIP搜索過程中發生錯誤: {str(clip_error)}")
                    return Response(
                        {"error": f"AI模型處理圖片時出錯: {str(clip_error)}", "success": False},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                # 使用產品適配器獲取詳細信息
                try:
                    product_adapter = ProductAdapter()
                    products = []
                    
                    # 導入商品模型類
                    from shopping_system.models import Product
                    
                    # 檢查產品數量
                    product_count = Product.objects.filter(is_active=True).count()
                    logger.info(f"資料庫中有 {product_count} 個活躍產品")
                    
                    for product_id in similar_ids:
                        try:
                            # 確保產品ID是整數
                            if isinstance(product_id, np.integer):
                                product_id = int(product_id)
                            logger.info(f"處理商品ID: {product_id}, 類型: {type(product_id)}")
                            
                            product = product_adapter.get_product_by_id(product_id, Product)
                            if product:  # 可能有些產品ID已不存在
                                products.append(product)
                            else:
                                logger.warning(f"找不到產品ID: {product_id}")
                        except Exception as prod_error:
                            logger.exception(f"獲取產品ID {product_id} 信息時出錯: {str(prod_error)}")
                            # 繼續處理其他產品，不中斷整個流程
                    
                    logger.info(f"返回產品數量: {len(products)}")
                    
                    # 如果沒有找到產品
                    if not products:
                        return Response({
                            "success": True,
                            "products": [],
                            "message": "找到相似商品ID，但無法獲取商品詳情",
                            "debug_info": {
                                "similar_ids": similar_ids,
                                "product_count": product_count
                            }
                        })
                    
                    return Response({
                        "success": True,
                        "products": products
                    })
                except Exception as adapter_error:
                    logger.exception(f"處理產品數據時發生錯誤: {str(adapter_error)}")
                    return Response(
                        {"error": f"處理產品數據時出錯: {str(adapter_error)}", "success": False},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            except Exception as inner_e:
                stack_trace = traceback.format_exc()
                logger.exception(f"處理圖片時發生內部異常:\n{stack_trace}")
                return Response(
                    {"error": f"處理圖片時出錯: {str(inner_e)}", "success": False, "stack_trace": stack_trace},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            finally:
                # 確保臨時文件被刪除
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                        logger.info(f"已刪除臨時文件: {temp_path}")
                    except Exception as del_error:
                        logger.error(f"刪除臨時文件時出錯: {str(del_error)}")
        except Exception as outer_e:
            stack_trace = traceback.format_exc()
            logger.exception(f"API視圖外層異常:\n{stack_trace}")
            return Response(
                {"error": f"處理請求時出錯: {str(outer_e)}", "success": False, "stack_trace": stack_trace},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )