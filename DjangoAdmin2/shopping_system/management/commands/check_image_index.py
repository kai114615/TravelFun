import os
import numpy as np
import logging
from django.core.management.base import BaseCommand
from django.db.models import Count
import faiss
from shopping_system.models import Product
from shopping_system.image_search.services.clip_search import get_clip_search

# 設置日誌格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '檢查圖像索引與商品數據的一致性'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='嘗試修復問題 (重建索引)'
        )

    def handle(self, *args, **options):
        fix_issues = options['fix']
        self.stdout.write(f"開始檢查圖像索引與商品數據的一致性（修復模式: {fix_issues}）...")
        
        # 獲取CLIP搜索實例
        clip_search = get_clip_search()
        
        # 檢查索引文件是否存在
        if not os.path.exists(clip_search.index_path) or not os.path.exists(clip_search.product_ids_path):
            self.stdout.write(self.style.ERROR(f"索引文件不存在: {clip_search.index_path} 或 {clip_search.product_ids_path}"))
            
            if fix_issues:
                self.stdout.write("嘗試構建索引...")
                from django.core.management import call_command
                call_command('build_image_index', force=True)
            return
        
        # 嘗試加載索引
        try:
            clip_search._load_index()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"無法加載索引: {str(e)}"))
            
            if fix_issues:
                self.stdout.write("嘗試構建索引...")
                from django.core.management import call_command
                call_command('build_image_index', force=True)
            return
        
        if clip_search.index is None or clip_search.product_ids is None:
            self.stdout.write(self.style.ERROR("索引加載失敗"))
            
            if fix_issues:
                self.stdout.write("嘗試構建索引...")
                from django.core.management import call_command
                call_command('build_image_index', force=True)
            return
        
        # 獲取當前產品數量
        active_products = Product.objects.filter(is_active=True)
        product_count = active_products.count()
        
        # 檢查索引大小
        index_size = clip_search.index.ntotal
        product_ids_count = len(clip_search.product_ids)
        
        self.stdout.write(f"活躍產品數量: {product_count}")
        self.stdout.write(f"索引大小: {index_size}")
        self.stdout.write(f"產品ID數量: {product_ids_count}")
        
        # 檢查不一致
        if index_size != product_ids_count:
            self.stdout.write(self.style.ERROR("索引大小與產品ID數量不一致！"))
            
            if fix_issues:
                self.stdout.write("嘗試重建索引...")
                from django.core.management import call_command
                call_command('build_image_index', force=True)
            return
        
        # 檢查索引中的產品ID是否存在於資料庫
        db_product_ids = set(active_products.values_list('id', flat=True))
        index_product_ids = set(clip_search.product_ids)
        
        missing_from_db = index_product_ids - db_product_ids
        missing_from_index = db_product_ids - index_product_ids
        
        if missing_from_db:
            self.stdout.write(self.style.WARNING(f"有 {len(missing_from_db)} 個產品ID在索引中，但不在資料庫中"))
            if len(missing_from_db) < 10:
                self.stdout.write(f"缺失的產品ID: {missing_from_db}")
            
        if missing_from_index:
            self.stdout.write(self.style.WARNING(f"有 {len(missing_from_index)} 個產品ID在資料庫中，但不在索引中"))
            if len(missing_from_index) < 10:
                self.stdout.write(f"缺失的產品ID: {missing_from_index}")
        
        # 檢查產品是否有圖片URL
        products_without_image = active_products.filter(image_url__isnull=True).count()
        if products_without_image > 0:
            self.stdout.write(self.style.WARNING(f"有 {products_without_image} 個產品沒有圖片URL"))
        
        products_with_empty_image = active_products.filter(image_url='').count()
        if products_with_empty_image > 0:
            self.stdout.write(self.style.WARNING(f"有 {products_with_empty_image} 個產品的圖片URL為空"))
        
        # 如果有不一致且啟用了修復模式
        if (missing_from_db or missing_from_index) and fix_issues:
            self.stdout.write("存在不一致，正在重建索引...")
            from django.core.management import call_command
            call_command('build_image_index', force=True)
        
        # 顯示索引文件大小
        index_file_size = os.path.getsize(clip_search.index_path) / (1024 * 1024)  # MB
        product_ids_file_size = os.path.getsize(clip_search.product_ids_path) / (1024 * 1024)  # MB
        
        self.stdout.write(f"索引文件大小: {index_file_size:.2f} MB")
        self.stdout.write(f"產品ID文件大小: {product_ids_file_size:.2f} MB")
        
        # 測試搜索功能
        self.stdout.write("測試搜索功能...")
        test_vector = np.random.randn(1, clip_search.index.d).astype('float32')
        test_vector = test_vector / np.linalg.norm(test_vector)
        
        try:
            scores, indices = clip_search.index.search(test_vector, 5)
            self.stdout.write(f"搜索測試成功，返回了 {len(indices[0])} 個結果")
            
            # 檢查測試結果中的產品ID是否存在
            test_product_ids = [clip_search.product_ids[idx] for idx in indices[0]]
            existing_products = Product.objects.filter(id__in=test_product_ids).count()
            
            self.stdout.write(f"測試結果中的產品ID: {test_product_ids}")
            self.stdout.write(f"其中 {existing_products} 個存在於資料庫")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"搜索測試失敗: {str(e)}"))
        
        # 提供總結
        if missing_from_db or missing_from_index or products_without_image > 0 or products_with_empty_image > 0:
            self.stdout.write(self.style.WARNING("檢查完成，發現一些不一致"))
            if fix_issues:
                self.stdout.write("已嘗試修復問題")
        else:
            self.stdout.write(self.style.SUCCESS("檢查完成，圖像索引與商品數據一致")) 