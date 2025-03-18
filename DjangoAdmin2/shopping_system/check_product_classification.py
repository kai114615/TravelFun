import os
import sys
import django
import re

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

# 導入模型
from shopping_system.models import Product, CategoryDisplay

# 定義各類別的關鍵詞
CATEGORY_KEYWORDS = {
    1: ['充氣床', '充氣墊', '睡墊', '充氣床墊', 'airbed', '懶人床', '空氣床'],  # 充氣床墊
    2: ['桌', '餐桌', '露營桌', '摺疊桌', '折疊桌', '戶外桌', '野餐桌', '蛋捲桌'],  # 露營桌
    3: ['帳篷', '天幕', '帳棚', '炊事帳', '客廳帳', '遮陽帳', 'tent', '蒙古包', '露營帳', '野餐帳'],  # 帳篷
    4: ['充電器', '充電頭', '變壓器', '充電線', '快充', '電源供應器', '充電座', '行動電源'],  # 充電器
    5: ['背包', '登山包', '後背包', '雙肩包', '背囊', '運動背包', '戶外包', '旅行包', '健行包'],  # 登山背包
    6: ['登山杖', '手杖', '拐杖', '健走杖', '登山手杖', '登山棍', '健行杖', '避震杖'],  # 登山杖
    7: ['手機', 'iphone', 'smartphone', '智慧型手機', '智慧手機', '5G手機', '4G手機'],  # 手機
    8: ['行李箱', '旅行箱', '拉桿箱', '登機箱', '托運箱', '硬殼箱', '軟殼箱', '萬向輪'],  # 行李箱
    9: ['爐', '瓦斯爐', '卡式爐', '瓦斯烤爐', '露營爐', '戶外爐具', '野炊爐', '登山爐']  # 瓦斯爐
}

# 反向查找類別ID對應的名稱
def get_category_name(category_id):
    category_names = {
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
    return category_names.get(category_id, f'未知類別({category_id})')

# 根據商品名稱和描述判斷可能的產品類型
def predict_product_type(name, description):
    if not name:
        return None
    
    # 商品名稱轉小寫以便比對
    name_lower = name.lower()
    desc_lower = description.lower() if description else ""
    
    # 儲存每個類別的匹配關鍵詞數量
    category_scores = {}
    
    for category_id, keywords in CATEGORY_KEYWORDS.items():
        # 計算該類別的關鍵詞在名稱和描述中出現的次數
        score = 0
        for keyword in keywords:
            if keyword.lower() in name_lower:
                score += 2  # 名稱中出現關鍵詞權重更高
            if keyword.lower() in desc_lower:
                score += 1  # 描述中出現關鍵詞權重低一些
        
        if score > 0:
            category_scores[category_id] = score
    
    # 如果有匹配的類別，返回得分最高的
    if category_scores:
        return max(category_scores.items(), key=lambda x: x[1])[0]
    
    return None

def check_product_classifications():
    """檢查所有商品的分類是否合理"""
    # 獲取所有活躍商品
    products = Product.objects.filter(is_active=True)
    print(f"共找到 {products.count()} 個活躍商品")
    
    # 存儲可能分類錯誤的商品
    misclassified_products = []
    
    for product in products:
        # 預測產品類型
        predicted_type = predict_product_type(product.name, product.description)
        
        # 如果預測類型與實際類型不符，且有預測結果
        if predicted_type and predicted_type != product.product_type_id:
            misclassified_products.append({
                'id': product.id,
                'name': product.name,
                'category': product.category,  # 這是品牌，而非類別
                'current_type_id': product.product_type_id,
                'current_type_name': get_category_name(product.product_type_id),
                'predicted_type_id': predicted_type,
                'predicted_type_name': get_category_name(predicted_type)
            })
    
    return misclassified_products

if __name__ == "__main__":
    print("開始檢查商品分類...")
    misclassified = check_product_classifications()
    
    if misclassified:
        print(f"\n找到 {len(misclassified)} 個可能分類錯誤的商品：")
        for idx, product in enumerate(misclassified, 1):
            print(f"\n{idx}. 商品ID: {product['id']}")
            print(f"   商品名稱: {product['name']}")
            print(f"   品牌: {product['category']}")
            print(f"   當前類型: {product['current_type_name']} (ID: {product['current_type_id']})")
            print(f"   預測類型: {product['predicted_type_name']} (ID: {product['predicted_type_id']})")
    else:
        print("未發現分類錯誤的商品。")
    
    print("\n檢查完成！") 