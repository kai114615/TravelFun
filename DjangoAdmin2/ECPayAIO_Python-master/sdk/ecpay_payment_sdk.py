# -*- coding: utf-8 -*-

import hashlib
import urllib.parse
from decimal import Decimal

class ECPayPaymentSdk:
    '''
    綠界金流 SDK
    '''

    def __init__(self, MerchantID, HashKey, HashIV):
        self.MerchantID = MerchantID
        self.HashKey = HashKey
        self.HashIV = HashIV

    def create_order(self, order_params):
        '''
        建立訂單
        '''
        # 檢查必填參數
        required_params = [
            'MerchantTradeNo',
            'MerchantTradeDate',
            'TotalAmount',
            'TradeDesc',
            'ItemName',
            'ReturnURL',
            'ChoosePayment'
        ]
        
        for param in required_params:
            if param not in order_params:
                raise Exception(f"訂單參數 '{param}' 為必填")
        
        # 加入MerchantID
        if 'MerchantID' not in order_params:
            order_params['MerchantID'] = self.MerchantID
            
        # 產生檢查碼
        check_mac_value = self.generate_check_mac_value(order_params)
        order_params['CheckMacValue'] = check_mac_value
        
        return order_params

    def generate_check_mac_value(self, params):
        '''
        產生檢查碼 - 嚴格按照綠界金流官方文檔標準
        參考文件: https://developers.ecpay.com.tw/?p=2866
        '''
        # 複製參數，避免修改原始參數
        params_copy = params.copy()
        
        # 移除不需要加入檢查碼的參數
        if 'CheckMacValue' in params_copy:
            del params_copy['CheckMacValue']
            
        # 將參數依照參數名稱的英文字母排序，由 A 到 Z 的順序排序（不區分大小寫）
        # 參考官方文檔：https://developers.ecpay.com.tw/?p=2902
        # 使用不區分大小寫的排序
        sorted_params = sorted(params_copy.items(), key=lambda x: x[0].lower())
        
        # 用 & 符號將所有參數串連起來
        param_string = "&".join([f"{key}={value}" for key, value in sorted_params])
        
        # 在最前面加上 HashKey，在最後面加上 HashIV
        check_string = f"HashKey={self.HashKey}&{param_string}&HashIV={self.HashIV}"
        
        # 調試輸出
        print("=== 綠界金流 CheckMacValue 生成過程 ===")
        print(f"1. 原始參數: {params_copy}")
        print(f"2. 排序後的參數: {sorted_params}")
        print(f"3. 參數串連: {param_string}")
        print(f"4. 加上 HashKey 和 HashIV: {check_string}")
        
        # 將整串字串進行 URL encode
        # 進行 URL encode 時，只需使用 utf-8 的編碼方式，將字串轉為 query string 的 資料型態
        # 由於 URL encode 後的字串會有小寫的情況，因此先轉成小寫，再進行 URL encode
        # 這是綠界特別要求的步驟
        check_string = check_string.lower()
        print(f"5. 轉小寫: {check_string}")
        
        # 使用 .NET 的 HttpUtility.UrlEncode (php 為 urlencode) 
        # 此處使用 Python 的 urllib.parse.quote_plus 來實現類似的功能
        check_string = urllib.parse.quote_plus(check_string)
        print(f"6. URL encode: {check_string}")
        
        # 將 + 號換成 %20 (綠界官方文檔特別要求)
        check_string = check_string.replace('+', '%20')
        print(f"7. 將 + 號換成 %20: {check_string}")
        
        # 使用 SHA256 壓碼
        check_mac_value = hashlib.sha256(check_string.encode('utf-8')).hexdigest()
        print(f"8. SHA256 hashlib: {check_mac_value}")
        
        # 轉大寫產生 CheckMacValue
        check_mac_value = check_mac_value.upper()
        print(f"9. 轉大寫產生 CheckMacValue: {check_mac_value}")
        print("========================================")
        
        return check_mac_value

    def gen_html_post_form(self, action_url, order_params):
        '''
        產生 HTML 的表單，用於提交到綠界金流
        '''
        html = f'''
        <form id="ecpay-form" method="post" action="{action_url}" style="display: none;">
        '''
        
        for key, value in order_params.items():
            html += f'<input type="hidden" name="{key}" value="{value}">\n'
            
        html += '''
        <input type="submit" value="送出訂單">
        </form>
        '''
        
        return html
