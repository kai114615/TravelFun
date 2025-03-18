import os
import sys
import django
import csv
from datetime import datetime
from collections import defaultdict

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

# 導入模型
from shopping_system.models import Product, CategoryDisplay

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

# 定義要修復的產品ID與正確的產品類型
# 這個字典將被用於自動修復已知的錯誤分類
PRODUCTS_TO_FIX = {
    266: 3,  # 戶外野餐帳 22-22022，應為帳篷(3)而非登山背包(5)
    # 從原先的腳本結果中添加其他需要修復的商品...
    271: 3,  # 應為帳篷類別
    270: 3,  # 應為帳篷類別
    272: 3,  # 應為帳篷類別
    276: 3,  # 應為帳篷類別
    265: 3,  # 應為帳篷類別
    251: 3,  # 應為帳篷類別
    247: 5,  # 應為登山背包類別
    241: 6,  # 應為登山杖類別
    192: 6,  # 應為登山杖類別
    190: 6,  # 應為登山杖類別
    193: 6,  # 應為登山杖類別
    194: 6,  # 應為登山杖類別
    191: 6,  # 應為登山杖類別
    186: 6,  # 應為登山杖類別
    195: 6,  # 應為登山杖類別
    197: 6,  # 應為登山杖類別
    243: 6,  # 應為登山杖類別
    242: 6,  # 應為登山杖類別
    196: 6,  # 應為登山杖類別
    244: 6,  # 應為登山杖類別
    246: 5,  # 應為登山背包類別
    248: 5,  # 應為登山背包類別
    249: 5,  # 應為登山背包類別
    250: 5,  # 應為登山背包類別
    204: 6,  # 應為登山杖類別
    174: 6,  # 應為登山杖類別
    273: 3,  # 應為帳篷類別
    274: 3,  # 應為帳篷類別
    275: 3,  # 應為帳篷類別
    198: 6,  # 應為登山杖類別
    189: 6,  # 應為登山杖類別
    187: 6,  # 應為登山杖類別
    188: 6,  # 應為登山杖類別
    185: 6,  # 應為登山杖類別
    223: 6,  # 應為登山杖類別
    222: 6,  # 應為登山杖類別
    207: 6,  # 應為登山杖類別
    206: 6,  # 應為登山杖類別
    224: 6,  # 應為登山杖類別
    208: 6,  # 應為登山杖類別
    205: 6,  # 應為登山杖類別
    221: 6,  # 應為登山杖類別
    225: 6,  # 應為登山杖類別
    245: 5,  # 應為登山背包類別
    259: 3,  # 應為帳篷類別
    260: 3,  # 應為帳篷類別
    263: 3,  # 應為帳篷類別
    264: 3,  # 應為帳篷類別
    261: 3,  # 應為帳篷類別
    262: 3,  # 應為帳篷類別
    200: 6,  # 應為登山杖類別
    199: 6,  # 應為登山杖類別
    203: 6,  # 應為登山杖類別
    202: 6,  # 應為登山杖類別
    201: 6,  # 應為登山杖類別
    173: 6,  # 應為登山杖類別
    172: 6,  # 應為登山杖類別
    177: 6,  # 應為登山杖類別
    175: 6,  # 應為登山杖類別
    183: 6,  # 應為登山杖類別
    179: 6,  # 應為登山杖類別
    180: 6,  # 應為登山杖類別
    181: 6,  # 應為登山杖類別
    182: 6,  # 應為登山杖類別
    176: 6,  # 應為登山杖類別
    178: 6,  # 應為登山杖類別
    184: 6,  # 應為登山杖類別
    220: 6,  # 應為登山杖類別
    209: 6,  # 應為登山杖類別
    210: 6,  # 應為登山杖類別
    211: 6,  # 應為登山杖類別
    219: 6,  # 應為登山杖類別
    218: 6,  # 應為登山杖類別
    217: 6,  # 應為登山杖類別
    215: 6,  # 應為登山杖類別
    216: 6,  # 應為登山杖類別
    214: 6,  # 應為登山杖類別
    213: 6,  # 應為登山杖類別
    212: 6   # 應為登山杖類別
}

def fix_product_classifications():
    """修復產品分類錯誤"""
    successful_updates = 0
    failed_updates = 0
    changes = defaultdict(int)  # 用於記錄分類變更統計
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"product_classification_fix_{timestamp}.log"
    
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write(f"開始修復產品分類錯誤 - {datetime.now()}\n")
        log.write("=" * 80 + "\n\n")
        
        for product_id, correct_type_id in PRODUCTS_TO_FIX.items():
            try:
                product = Product.objects.get(id=product_id)
                old_type_id = product.product_type_id
                old_type_name = get_category_name(old_type_id)
                new_type_name = get_category_name(correct_type_id)
                
                # 執行更新
                product.product_type_id = correct_type_id
                product.save()
                
                # 記錄成功
                log_message = (f"✅ 成功更新商品 ID {product_id}: \"{product.name}\"\n"
                              f"   從 {old_type_name}(ID:{old_type_id}) → "
                              f"{new_type_name}(ID:{correct_type_id})\n")
                log.write(log_message)
                print(log_message)
                
                # 更新統計資料
                successful_updates += 1
                change_key = f"{old_type_name} → {new_type_name}"
                changes[change_key] += 1
                
            except Product.DoesNotExist:
                # 記錄失敗 - 找不到產品
                log_message = f"❌ 錯誤: 找不到ID為 {product_id} 的商品\n"
                log.write(log_message)
                print(log_message)
                failed_updates += 1
                
            except Exception as e:
                # 記錄其他錯誤
                log_message = f"❌ 錯誤: 更新ID為 {product_id} 的商品時發生錯誤: {str(e)}\n"
                log.write(log_message)
                print(log_message)
                failed_updates += 1
        
        # 寫入摘要
        summary = (f"\n\n修復完成摘要:\n"
                  f"總共嘗試修復: {len(PRODUCTS_TO_FIX)} 個商品\n"
                  f"成功更新: {successful_updates} 個商品\n"
                  f"失敗: {failed_updates} 個商品\n\n")
        log.write(summary)
        print(summary)
        
        # 寫入分類變更統計
        if changes:
            log.write("分類變更統計:\n")
            for change, count in sorted(changes.items(), key=lambda x: x[1], reverse=True):
                change_stat = f"{change}: {count} 個商品\n"
                log.write(change_stat)
                print(change_stat)
    
    return {
        'successful': successful_updates,
        'failed': failed_updates,
        'total': len(PRODUCTS_TO_FIX),
        'changes': dict(changes),
        'log_file': log_file
    }

# 定義改進的商品分類關鍵詞
CATEGORY_KEYWORDS = {
    1: {  # 充氣床墊
        'primary': ['充氣床墊', '充氣床', '空氣床', 'airbed', '懶人床', '充氣式床墊'],
        'secondary': ['睡墊', '充氣墊', '露營床', '充氣', '充氣式', '自動充氣', '車中床', '睡舖', '帳內床墊'],
        'negative': ['桌', '帳篷', '手機', '電腦', '手杖', '行李箱', '瓦斯']
    },
    2: {  # 露營桌
        'primary': ['桌', '餐桌', '露營桌', '摺疊桌', '折疊桌', '蛋捲桌', '野餐桌'],
        'secondary': ['露營桌椅', '書桌', '茶几', '方桌', '圓桌', '折合桌', '桌子', '旅行桌', '行動桌'],
        'negative': ['床', '帳篷', '手機', '背包', '杖', '爐', '電器']
    },
    3: {  # 帳篷
        'primary': ['帳篷', '露營帳', '天幕', '帳棚', '炊事帳', '客廳帳', 'tent', '露營帳篷', '速開帳', '野餐帳'],
        'secondary': ['遮陽帳', '蒙古包', '野餐帳', '戶外帳', '帳篷式', '帳內', '營帳', '野營帳'],
        'negative': ['床', '桌', '手機', '充電器', '登山杖', '除非是配件組合']
    },
    4: {  # 充電器
        'primary': ['充電器', '充電頭', '變壓器', 'GaN', '氮化鎵', '快充', '充電座', '行動電源'],
        'secondary': ['充電線', '電源供應器', '電源適配器', '快速充電', 'PD充電', '電源插頭', 'Type-C'],
        'negative': ['手機本身', '床', '桌', '爐', '除非是配件組合']
    },
    5: {  # 登山背包
        'primary': ['背包', '登山包', '後背包', '雙肩包', '背囊', '書包', '旅行包', '健行包'],
        'secondary': ['運動背包', '戶外包', '戶外背包', '行李包', '登山背包', '攀登包', '徒步包', '包包'],
        'negative': ['床', '桌', '帳篷', '充電器', '手機', '行李箱', '爐', '野餐帳', '除非是配件組合']
    },
    6: {  # 登山杖
        'primary': ['登山杖', '手杖', '拐杖', '健走杖', '避震杖', '登山棍', '健行杖'],
        'secondary': ['碳纖維杖', '鋁合金杖', '三節杖', '折疊杖', '伸縮杖', '登山手杖', '杖子'],
        'negative': ['床', '桌', '帳篷', '充電器', '背包', '行李箱', '爐']
    },
    7: {  # 手機
        'primary': ['手機', 'iphone', 'smartphone', 'phone', '智慧型手機', '智慧手機', 'android'],
        'secondary': ['5G手機', '4G手機', '智能手機', '通訊設備', '行動電話', '蘋果手機', '三星手機'],
        'negative': ['充電器', '如果是充電配件則為充電器類別', '手機殼', '手機套', '手機架']
    },
    8: {  # 行李箱
        'primary': ['行李箱', '旅行箱', '拉桿箱', '登機箱', '托運箱', '硬殼箱', '軟殼箱'],
        'secondary': ['萬向輪', '箱子', '旅行行李箱', '旅遊箱', '胖胖箱', '20吋', '24吋', '28吋'],
        'negative': ['床', '桌', '帳篷', '充電器', '背包', '登山杖', '爐']
    },
    9: {  # 瓦斯爐
        'primary': ['瓦斯爐', '卡式爐', '瓦斯烤爐', '露營爐', '戶外爐具', '野炊爐', '登山爐'],
        'secondary': ['爐', '爐具', '烤肉爐', '燒烤爐', '炊具', '烹飪爐', '瓦斯', '炊事爐'],
        'negative': ['床', '桌', '帳篷', '充電器', '背包', '登山杖', '行李箱', '除非是配件組合']
    }
}

def predict_product_type_improved(name, description, brand):
    """使用改進的關鍵詞和權重系統預測產品類型"""
    if not name:
        return None, 0
    
    # 商品名稱和描述轉小寫以便比對
    name_lower = name.lower() if name else ""
    desc_lower = description.lower() if description else ""
    brand_lower = brand.lower() if brand else ""
    
    # 將所有文本合併為一個完整字符串用於分析（帶權重）
    full_text = name_lower + " " + name_lower + " " + desc_lower
    
    # 記錄每個分類的得分
    category_scores = {}
    
    # 應用特殊規則處理特定案例
    # 例如：如果名稱包含"充電器"和"手機"，則很可能是充電器而不是手機
    is_likely_charger = False
    for charger_term in ['充電器', '充電頭', '變壓器', 'GaN', '氮化鎵', '快充', 'Type-C']:
        if charger_term.lower() in name_lower:
            is_likely_charger = True
            break
    
    # 計算每個類別的得分
    for category_id, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        
        # 檢查主要關鍵詞（高權重）
        for keyword in keywords['primary']:
            if keyword.lower() in name_lower:
                score += 10  # 名稱中的主要關鍵詞權重最高
            if keyword.lower() in desc_lower:
                score += 3   # 描述中的主要關鍵詞權重較高
        
        # 檢查次要關鍵詞（中等權重）
        for keyword in keywords['secondary']:
            if keyword.lower() in name_lower:
                score += 5   # 名稱中的次要關鍵詞權重中等
            if keyword.lower() in desc_lower:
                score += 2   # 描述中的次要關鍵詞權重低一些
        
        # 檢查負向關鍵詞（扣分）
        for keyword in keywords['negative']:
            if keyword.lower() in name_lower:
                # 如果商品名稱可能是組合產品，則不要過度扣分
                if "組合" in name_lower or "套裝" in name_lower or "組" in name_lower:
                    score -= 1
                else:
                    score -= 3
        
        # 應用特殊規則
        if is_likely_charger and category_id == 4:  # 如果看起來是充電器且正在計算充電器類別
            score += 8
        elif is_likely_charger and category_id == 7:  # 如果看起來是充電器但正在計算手機類別
            score -= 5
        
        # 特殊處理帳篷與登山背包的混淆情況
        if "野餐帳" in name_lower and category_id == 3:
            score += 15  # 明確提到"野餐帳"的產品應該是帳篷
        
        # 記錄得分
        if score > 0:
            category_scores[category_id] = score
    
    # 如果有匹配的類別，找出得分最高的
    if category_scores:
        best_category_id = max(category_scores.items(), key=lambda x: x[1])[0]
        confidence_score = category_scores[best_category_id]
        return best_category_id, confidence_score
    
    return None, 0

def check_product_classifications_improved():
    """使用改進的算法檢查所有商品的分類"""
    # 獲取所有活躍商品
    products = Product.objects.filter(is_active=True)
    print(f"共找到 {products.count()} 個活躍商品")
    
    # 存儲可能分類錯誤的商品
    misclassified_products = []
    
    # 存儲各類型錯誤數量的統計
    error_by_type = defaultdict(int)
    
    # 存儲高置信度錯誤
    high_confidence_errors = []
    medium_confidence_errors = []
    low_confidence_errors = []
    
    for product in products:
        # 預測產品類型及置信度
        predicted_type, confidence = predict_product_type_improved(
            product.name, product.description, product.category
        )
        
        # 如果預測類型與實際類型不符，且有預測結果
        if predicted_type and predicted_type != product.product_type_id:
            error_info = {
                'id': product.id,
                'name': product.name,
                'brand': product.category,
                'current_type_id': product.product_type_id,
                'current_type_name': get_category_name(product.product_type_id),
                'predicted_type_id': predicted_type,
                'predicted_type_name': get_category_name(predicted_type),
                'confidence': confidence
            }
            
            misclassified_products.append(error_info)
            
            # 記錄錯誤類型
            error_key = f"{error_info['current_type_name']} → {error_info['predicted_type_name']}"
            error_by_type[error_key] += 1
            
            # 根據置信度分類錯誤
            if confidence >= 15:
                high_confidence_errors.append(error_info)
            elif confidence >= 10:
                medium_confidence_errors.append(error_info)
            else:
                low_confidence_errors.append(error_info)
    
    # 分類結果
    return {
        'all_errors': misclassified_products,
        'error_by_type': dict(error_by_type),
        'high_confidence_errors': high_confidence_errors,
        'medium_confidence_errors': medium_confidence_errors,
        'low_confidence_errors': low_confidence_errors
    }

def export_errors_to_csv(errors, filename):
    """將錯誤導出到CSV文件"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'name', 'brand', 'current_type_id', 'current_type_name', 
                      'predicted_type_id', 'predicted_type_name', 'confidence']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for error in errors:
            writer.writerow(error)
    
    print(f"已導出 {len(errors)} 條錯誤記錄到 {filename}")

def generate_fix_dict(errors, min_confidence=15):
    """根據檢測結果生成修復字典"""
    fix_dict = {}
    for error in errors:
        if error['confidence'] >= min_confidence:
            fix_dict[error['id']] = error['predicted_type_id']
    
    # 生成可複製的字典代碼
    result = "PRODUCTS_TO_FIX = {\n"
    for product_id, type_id in sorted(fix_dict.items()):
        result += f"    {product_id}: {type_id},  # 應為{get_category_name(type_id)}類別\n"
    result += "}"
    
    return result

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='商品分類管理工具')
    parser.add_argument('--action', choices=['check', 'fix', 'both'], default='both',
                        help='執行動作: check (僅檢查), fix (僅修復), both (檢查並修復)')
    parser.add_argument('--min-confidence', type=int, default=15,
                        help='最小置信度閾值，用於識別高置信度錯誤')
    
    args = parser.parse_args()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 執行修復
    if args.action in ['fix', 'both']:
        print("開始修復已知的商品分類錯誤...")
        fix_results = fix_product_classifications()
        print(f"修復完成! 詳細日誌已保存至 {fix_results['log_file']}")
    
    # 執行檢查
    if args.action in ['check', 'both']:
        print("\n開始進行改進後的商品分類檢查...")
        results = check_product_classifications_improved()
        
        all_errors = results['all_errors']
        high_confidence = results['high_confidence_errors']
        medium_confidence = results['medium_confidence_errors']
        low_confidence = results['low_confidence_errors']
        
        print(f"\n找到 {len(all_errors)} 個可能分類錯誤的商品：")
        print(f"- 高置信度錯誤: {len(high_confidence)} 個")
        print(f"- 中置信度錯誤: {len(medium_confidence)} 個")
        print(f"- 低置信度錯誤: {len(low_confidence)} 個")
        
        print("\n錯誤類型統計:")
        for error_type, count in sorted(results['error_by_type'].items(), key=lambda x: x[1], reverse=True):
            print(f"{error_type}: {count} 個商品")
        
        # 輸出高置信度錯誤詳情
        if high_confidence:
            print("\n高置信度錯誤詳情:")
            for idx, error in enumerate(high_confidence, 1):
                print(f"\n{idx}. 商品ID: {error['id']}")
                print(f"   商品名稱: {error['name']}")
                print(f"   品牌: {error['brand']}")
                print(f"   當前類型: {error['current_type_name']} (ID: {error['current_type_id']})")
                print(f"   預測類型: {error['predicted_type_name']} (ID: {error['predicted_type_id']})")
                print(f"   置信度: {error['confidence']}")
        
        # 導出結果到CSV文件
        if all_errors:
            csv_filename = f"classification_errors_{timestamp}.csv"
            export_errors_to_csv(all_errors, csv_filename)
            print(f"\n檢查結果已導出到: {csv_filename}")
            
            # 生成修復字典
            fix_dict_text = generate_fix_dict(high_confidence, args.min_confidence)
            fix_dict_file = f"suggested_fixes_{timestamp}.py"
            with open(fix_dict_file, 'w', encoding='utf-8') as f:
                f.write(fix_dict_text)
            
            print(f"建議的修復字典已保存至: {fix_dict_file}")
        
        print("\n檢查完成！") 