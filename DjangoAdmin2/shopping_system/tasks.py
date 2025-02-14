import json
import os
import asyncio
import aiofiles
from celery import shared_task
from django.core.cache import cache
from django.apps import apps
from collections import defaultdict

@shared_task
def update_json_file_async():
    """異步更新JSON檔案的Celery任務"""
    try:
        # 使用緩存防止重複更新
        if cache.get('updating_json'):
            return
        cache.set('updating_json', True, timeout=60)  # 設置60秒鎖定

        # 動態獲取Product模型
        Product = apps.get_model('shopping_system', 'Product')

        # 獲取所有商品資料
        products = Product.objects.all()
        products_data = []
        for product in products:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'category': product.category,
                'price': str(product.price),
                'description': product.description,
                'stock': product.stock,
                'is_active': product.is_active,
                'image_url': product.get_image_url(),
                'created_at': product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': product.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })

        # 構建JSON檔案路徑
        json_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'src', 'views', 'front', 'Mall', 'data', 'MallProduct.json'
        )

        # 使用異步IO寫入檔案
        async def write_json():
            async with aiofiles.open(json_file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(products_data, ensure_ascii=False, indent=2))

        # 執行異步寫入
        asyncio.run(write_json())

        # 更新類別資料
        update_categories_json.delay()

        return {
            'status': 'success',
            'message': f'成功更新 {len(products_data)} 筆商品資料',
            'total_products': len(products_data)
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
    finally:
        cache.delete('updating_json')

@shared_task
def update_categories_json():
    """更新商品類別JSON檔案"""
    try:
        # 讀取 MallProduct.json
        json_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'src', 'views', 'front', 'Mall', 'data', 'MallProduct.json'
        )
        
        with open(json_file_path, 'r', encoding='utf-8') as f:
            products = json.load(f)

        # 使用defaultdict收集類別和品牌
        categories_dict = defaultdict(set)
        
        # 分析所有商品的類別
        for product in products:
            category = product['category']
            # 根據類別名稱生成ID (轉換為小寫並用底線連接)
            category_id = '_'.join(category.lower().split())
            categories_dict[category_id].add(category)

        # 準備categories資料結構
        categories_data = {
            "categories": [
                {
                    "id": category_id,
                    "name": list(category_names)[0],  # 使用第一個名稱作為顯示名稱
                    "brands": sorted(list(category_names))  # 將所有變體作為品牌
                }
                for category_id, category_names in categories_dict.items()
            ]
        }

        # 將類別按照name排序
        categories_data["categories"].sort(key=lambda x: x["name"])

        # 構建categories.json檔案路徑
        categories_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'src', 'views', 'front', 'Mall', 'data', 'categories.json'
        )

        # 寫入categories.json
        async def write_categories():
            async with aiofiles.open(categories_file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(categories_data, ensure_ascii=False, indent=2))

        # 執行異步寫入
        asyncio.run(write_categories())

        return {
            'status': 'success',
            'message': f'成功更新商品類別資料，共 {len(categories_data["categories"])} 個類別'
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        } 