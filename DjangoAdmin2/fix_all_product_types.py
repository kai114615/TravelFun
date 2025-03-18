import os
import sys
import django
import json
from datetime import datetime

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

# 導入模型
from shopping_system.models import Product
from check_product_classification import check_product_classifications, get_category_name

def fix_all_product_types(auto_fix=False):
    """檢查並修復所有商品的分類錯誤"""
    print("開始檢查商品分類...")
    misclassified = check_product_classifications()
    
    if not misclassified:
        print("未發現分類錯誤的商品。")
        return
    
    print(f"\n找到 {len(misclassified)} 個可能分類錯誤的商品：")
    
    # 生成報告
    report = []
    for idx, product in enumerate(misclassified, 1):
        print(f"\n{idx}. 商品ID: {product['id']}")
        print(f"   商品名稱: {product['name']}")
        print(f"   品牌: {product['category']}")
        print(f"   當前類型: {product['current_type_name']} (ID: {product['current_type_id']})")
        print(f"   預測類型: {product['predicted_type_name']} (ID: {product['predicted_type_id']})")
        
        report.append(product)
    
    # 保存報告到文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"product_classification_report_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n分類報告已保存到文件: {filename}")
    
    # 如果啟用自動修復，則修改所有錯誤分類的商品
    if auto_fix:
        print("\n開始自動修復商品分類...")
        fixed_count = 0
        
        for product_info in misclassified:
            try:
                # 獲取數據庫中的產品對象
                product = Product.objects.get(id=product_info['id'])
                
                # 更新產品類型
                old_type = product.product_type_id
                product.product_type_id = product_info['predicted_type_id']
                product.save()
                
                print(f"已修復商品 ID {product.id}: '{product.name}' 的類型從 {get_category_name(old_type)} 更改為 {get_category_name(product.product_type_id)}")
                fixed_count += 1
                
            except Product.DoesNotExist:
                print(f"錯誤: 找不到 ID {product_info['id']} 的商品")
            except Exception as e:
                print(f"修復商品 ID {product_info['id']} 時出錯: {str(e)}")
        
        print(f"\n修復完成，成功修復 {fixed_count}/{len(misclassified)} 個商品的分類。")
    else:
        print("\n若要自動修復所有錯誤分類，請使用參數 --auto-fix 再次運行此腳本。")
        print("例如: python fix_all_product_types.py --auto-fix")

if __name__ == "__main__":
    # 檢查是否啟用自動修復
    auto_fix = "--auto-fix" in sys.argv
    
    if auto_fix:
        print("⚠️ 警告: 將自動修復所有分類錯誤的商品 ⚠️")
        confirmation = input("確定要繼續嗎? (y/n): ")
        
        if confirmation.lower() != 'y':
            print("操作已取消")
            sys.exit(0)
    
    fix_all_product_types(auto_fix) 