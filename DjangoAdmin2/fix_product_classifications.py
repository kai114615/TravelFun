import os
import sys
import django
import time

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

# 導入模型
from shopping_system.models import Product

# 需要修復的商品ID及其正確的product_type_id
PRODUCTS_TO_FIX = {
    # ID 266 (特別關注的商品)
    266: 3,  # 戶外野餐帳應該是帳篷(3)而不是登山背包(5)
    
    # 以下是檢查腳本發現的錯誤分類商品
    110: 9,  # 瓦斯爐
    161: 3,  # 帳篷
    175: 3,  # 帳篷
    191: 3,  # 帳篷
    207: 1,  # 充氣床墊
    233: 3,  # 帳篷
    269: 3,  # 帳篷
    270: 3,  # 帳篷
    278: 3,  # 帳篷
    280: 3,  # 帳篷(天幕)
    282: 1,  # 充氣床墊
    284: 1,  # 充氣床墊
    309: 1,  # 充氣床墊
    325: 1,  # 充氣床墊
    338: 1,  # 充氣床墊
    341: 1,  # 充氣床墊
    346: 1,  # 充氣床墊
    347: 1,  # 充氣床墊
    398: 1,  # 充氣床墊
    410: 1,  # 充氣床墊
    450: 1,  # 充氣床墊
    532: 8,  # 行李箱
    659: 7,  # 手機
    679: 7,  # 手機
    680: 7,  # 手機
    739: 7,  # 手機
    784: 2,  # 露營桌
    792: 2,  # 露營桌
    803: 2,  # 露營桌
    810: 2,  # 露營桌
    813: 2,  # 露營桌
    817: 2,  # 露營桌
    825: 2,  # 露營桌
    827: 2,  # 露營桌
    828: 2,  # 露營桌
    851: 2,  # 露營桌
    871: 4,  # 充電器
    872: 4,  # 充電器
    873: 4,  # 充電器
    875: 4,  # 充電器
    876: 4,  # 充電器
    881: 4,  # 充電器
    889: 4,  # 充電器
    893: 4,  # 充電器
    895: 4,  # 充電器
    897: 4,  # 充電器
    900: 4,  # 充電器
    901: 4,  # 充電器
    902: 4,  # 充電器
    903: 4,  # 充電器
    905: 4,  # 充電器
    909: 4,  # 充電器
    910: 4,  # 充電器
    920: 4,  # 充電器
    925: 4,  # 充電器
    931: 4,  # 充電器
    932: 4,  # 充電器
    933: 4,  # 充電器
    935: 4,  # 充電器
    948: 4,  # 充電器
    956: 4,  # 充電器
    961: 4,  # 充電器
    962: 4,  # 充電器
    963: 4,  # 充電器
    965: 4,  # 充電器
    970: 4,  # 充電器
    978: 4,  # 充電器
    981: 4,  # 充電器
    991: 4,  # 充電器
    992: 4,  # 充電器
    993: 4,  # 充電器
    1000: 4,  # 充電器
    1004: 4,  # 充電器
    1007: 4,  # 充電器
    1010: 4,  # 充電器
    1052: 6,  # 登山杖
    1071: 6,  # 登山杖
    1112: 6,  # 登山杖
    1136: 6,  # 登山杖
    1274: 5,  # 登山背包
}

# 分類ID對應的名稱，用於日誌輸出
CATEGORY_NAMES = {
    1: '充氣床墊',
    2: '露營桌',
    3: '帳篷',
    4: '充電器',
    5: '登山背包',
    6: '登山杖',
    7: '手機',
    8: '行李箱',
    9: '瓦斯爐'
}

def fix_product_classifications():
    """批量修復分類錯誤的商品"""
    print(f"開始修復 {len(PRODUCTS_TO_FIX)} 個分類錯誤的商品...\n")
    
    # 記錄成功和失敗的修復
    success_count = 0
    failed_ids = []
    
    # 按類別分組的計數
    category_changes = {}
    
    for product_id, correct_type_id in PRODUCTS_TO_FIX.items():
        try:
            product = Product.objects.get(id=product_id)
            old_type_id = product.product_type_id
            
            # 記錄原始分類到新分類的轉換
            key = f"{CATEGORY_NAMES.get(old_type_id, f'未知({old_type_id})')} → {CATEGORY_NAMES.get(correct_type_id, f'未知({correct_type_id})')}"
            if key not in category_changes:
                category_changes[key] = 0
            category_changes[key] += 1
            
            # 更新產品類型
            product.product_type_id = correct_type_id
            product.save()
            
            print(f"✅ 成功修復 ID {product_id}: {product.name}")
            print(f"   從 {CATEGORY_NAMES.get(old_type_id, f'未知({old_type_id})')} 改為 {CATEGORY_NAMES.get(correct_type_id, f'未知({correct_type_id})')}")
            success_count += 1
            
        except Product.DoesNotExist:
            print(f"❌ 錯誤：找不到 ID {product_id} 的商品")
            failed_ids.append(product_id)
        except Exception as e:
            print(f"❌ 錯誤：修復 ID {product_id} 時出現問題: {str(e)}")
            failed_ids.append(product_id)
    
    # 輸出統計信息
    print("\n修復完成！統計信息：")
    print(f"總計 {len(PRODUCTS_TO_FIX)} 個商品，成功修復 {success_count} 個，失敗 {len(failed_ids)} 個")
    
    if category_changes:
        print("\n分類變更統計：")
        for change, count in sorted(category_changes.items(), key=lambda x: x[1], reverse=True):
            print(f"{change}: {count} 個商品")
    
    if failed_ids:
        print("\n以下商品修復失敗：")
        for failed_id in failed_ids:
            print(f"- ID {failed_id}")
    
    return success_count, len(failed_ids)

if __name__ == "__main__":
    print("開始修復商品分類錯誤...")
    success, failed = fix_product_classifications()
    print(f"\n修復程序執行完畢: 成功 {success} 個，失敗 {failed} 個。") 