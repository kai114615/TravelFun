import os
import sys
import django
import time

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

# 導入模型
from shopping_system.models import Product

def fix_product_type():
    """修復產品類型錯誤"""
    try:
        # 修復 ID 266 的產品類型
        product = Product.objects.get(id=266)
        old_type = product.product_type_id
        
        print(f"找到產品 ID 266: {product.name}")
        print(f"當前產品類型: {old_type}")
        
        # 更新產品類型
        product.product_type_id = 3  # 設置為帳篷類型
        product.save()
        
        print(f"已成功將產品 '{product.name}' 的類型從 {old_type} 修改為 3 (帳篷)")
        return True
    except Product.DoesNotExist:
        print("找不到 ID 266 的產品")
        return False
    except Exception as e:
        print(f"修復產品類型時出錯: {str(e)}")
        return False

if __name__ == "__main__":
    print("開始修復產品類型...")
    success = fix_product_type()
    if success:
        print("修復完成！")
    else:
        print("修復失敗。") 