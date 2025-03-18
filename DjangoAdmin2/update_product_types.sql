-- 清空現有分類（可選）
UPDATE shopping_system_product SET product_type_id = NULL;

-- 1. 充氣床墊類別 (ID=1)
UPDATE shopping_system_product 
SET product_type_id = 1
WHERE 
  category IN ('YAKIMA', 'MBCF 露營狂', 'INTEX 原廠公司貨', 'FJ', 'DREAMCATCHER', 'Aerogogo', 'Lumikenka 露米', 'Naturehike', 'LIFECODE')
  OR name LIKE '%充氣床%' 
  OR name LIKE '%床墊%' 
  OR name LIKE '%睡墊%'
  OR name LIKE '%氣墊床%';

-- 2. 露營桌類別 (ID=2)
UPDATE shopping_system_product 
SET product_type_id = 2
WHERE 
  category IN ('IHouse', 'Nature Concept', 'C&B', '酷博士', 'Besthot', 'Lexiang樂享', '匠俱', 'hoi! 好好生活', 'CGW', 'NITORI 宜得利家居', 'LOGIS', 'E.C outdoor', '露營達人', '家居生活館', '多瓦娜', 'WAKUHOME 瓦酷家具', 'ONE 生活')
  OR name LIKE '%露營桌%' 
  OR name LIKE '%折疊桌%' 
  OR name LIKE '%摺疊桌%'
  OR name LIKE '%野餐桌%';

-- 3. 帳篷類別 (ID=3)
UPDATE shopping_system_product 
SET product_type_id = 3
WHERE 
  category IN ('MBCF 露營狂', 'Coleman', 'KAZMI', 'LIFECODE', 'ADISI', 'RHINO 犀牛', 'ATUNAS 歐都納', 'SNOW PEAK', '速可搭', '野樂', '野道家', '山林者', '戶外專家', '大營家', '野放', '野道', '野趣', '野遊')
  OR name LIKE '%帳篷%' 
  OR name LIKE '%天幕%' 
  OR name LIKE '%帳棚%'
  OR name LIKE '%營柱%';

-- 4. 充電器類別 (ID=4)
UPDATE shopping_system_product 
SET product_type_id = 4
WHERE 
  category IN ('+886', 'ADAM', 'Acer', 'ASUS', 'Apple', 'Baseus', 'Belkin', 'BSMI', 'CITY', 'DELL', 'ENERGEAR', 'HANG', 'HP', 'HUAWEI', 'KINYO', 'Lenovo', 'LG', 'Moshi', 'OPPO', 'PHILIPS', 'PowerFalcon', 'PROBOX', 'REMAX', 'Samsung', 'SONY', 'TOTU', 'TYLT', 'UAG', 'UGREEN', 'VIVO', 'Xmart', 'ZMI紫米', '亞果元素', '安伯特', '小米', '快譯通', '技嘉', '東元', '飛利浦', '勳風', '聯想', '羅技', '魔淇')
  OR name LIKE '%充電器%' 
  OR name LIKE '%電源%' 
  OR name LIKE '%行動電源%'
  OR name LIKE '%變壓器%';

-- 5. 登山背包類別 (ID=5)
UPDATE shopping_system_product 
SET product_type_id = 5
WHERE 
  category IN ('Horizon 天際線', 'SHANER', 'DIBOTE 迪伯特', 'PolarStar 桃源戶外', 'The North Face 官方旗艦', 'Gregory', 'KAKA', 'Jack wolfskin 飛狼', 'ATUNAS 歐都納', 'AOKING')
  OR name LIKE '%登山背包%' 
  OR name LIKE '%背包%' 
  OR name LIKE '%健行包%' 
  OR name LIKE '%戶外包%';

-- 6. 登山杖類別 (ID=6)
UPDATE shopping_system_product 
SET product_type_id = 6
WHERE 
  category IN ('ProPACER', 'ATUNAS 歐都納', 'FIZAN', 'Horizon 天際線', 'Xavagear', 'SELPA', 'Pioneer 開拓者', 'Ta-Da 泰達', 'OUTSY', 'May Shop', 'S.Motus', 'MASTERS', 'Naturehike')
  OR name LIKE '%登山杖%' 
  OR name LIKE '%健行杖%' 
  OR name LIKE '%避震杖%'
  OR name LIKE '%徒步杖%';

-- 7. 手機類別 (ID=7)
UPDATE shopping_system_product 
SET product_type_id = 7
WHERE 
  category IN ('HTC 宏達電', 'realme', 'ASUS 華碩', 'OPPO', 'POCO', '小米', 'Apple', 'vivo', 'Samsung 三星', 'Motorola')
  OR name LIKE '%手機%' 
  OR name LIKE '%iPhone%' 
  OR name LIKE '%智慧型手機%'
  OR name LIKE '%智能手機%';

-- 8. 行李箱類別 (ID=8)
UPDATE shopping_system_product 
SET product_type_id = 8
WHERE 
  category IN ('Arowana 亞諾納', 'American Explorer', 'eminent 萬國通路', 'FJ', 'ALLEZ 奧莉薇閣', 'Mr.Box', 'Deseno 笛森諾', '路比達', 'LUDWIN 路德威')
  OR name LIKE '%行李箱%' 
  OR name LIKE '%旅行箱%' 
  OR name LIKE '%拉桿箱%'
  OR name LIKE '%登機箱%';

-- 9. 瓦斯爐類別 (ID=9)
UPDATE shopping_system_product 
SET product_type_id = 9
WHERE 
  category IN ('Pro Kamping 領航家', 'Iwatani 岩谷', 'Dr.Hows', '妙管家', '勳風', '日本BRUNO', 'Jo Go Wu', 'Snow Peak', 'COTD', 'Camping Ace')
  OR name LIKE '%瓦斯爐%' 
  OR name LIKE '%卡式爐%' 
  OR name LIKE '%爐具%'
  OR name LIKE '%炊具%';

-- 處理描述欄位中的關鍵詞（較低優先級）
UPDATE shopping_system_product 
SET product_type_id = 1
WHERE 
  product_type_id IS NULL AND 
  (description LIKE '%充氣床%' OR description LIKE '%睡墊%');

UPDATE shopping_system_product 
SET product_type_id = 3
WHERE 
  product_type_id IS NULL AND 
  (description LIKE '%帳篷%' OR description LIKE '%露營%' OR description LIKE '%天幕%');

UPDATE shopping_system_product 
SET product_type_id = 9
WHERE 
  product_type_id IS NULL AND 
  (description LIKE '%炊煮%' OR description LIKE '%卡式爐%' OR description LIKE '%瓦斯爐%');

-- 特殊品牌處理（與其它品牌重複但屬於特定類別的情況）
UPDATE shopping_system_product 
SET product_type_id = 9
WHERE 
  category = 'Snow Peak' AND
  (name LIKE '%爐%' OR name LIKE '%炊%');

UPDATE shopping_system_product 
SET product_type_id = 3
WHERE 
  category = 'Snow Peak' AND
  (name LIKE '%帳%' OR name LIKE '%營%');

-- 特殊品牌處理：其他跨類別品牌

-- 1. Naturehike 品牌的特殊處理
UPDATE shopping_system_product 
SET product_type_id = 1  -- 充氣床墊
WHERE 
  category = 'Naturehike' AND
  (name LIKE '%床%' OR name LIKE '%墊%' OR name LIKE '%睡%');

UPDATE shopping_system_product 
SET product_type_id = 6  -- 登山杖
WHERE 
  category = 'Naturehike' AND
  (name LIKE '%杖%' OR name LIKE '%登山杖%');

-- 2. ATUNAS 歐都納的特殊處理（更精確區分）
UPDATE shopping_system_product 
SET product_type_id = 3  -- 帳篷
WHERE 
  category = 'ATUNAS 歐都納' AND
  (name LIKE '%帳篷%' OR name LIKE '%天幕%' OR name LIKE '%帳棚%');

UPDATE shopping_system_product 
SET product_type_id = 5  -- 登山背包
WHERE 
  category = 'ATUNAS 歐都納' AND
  (name LIKE '%背包%' OR name LIKE '%包%') AND
  name NOT LIKE '%睡袋%';  -- 避免與睡袋混淆

UPDATE shopping_system_product 
SET product_type_id = 6  -- 登山杖
WHERE 
  category = 'ATUNAS 歐都納' AND
  (name LIKE '%杖%' OR name LIKE '%登山杖%');

-- 3. FJ 品牌的特殊處理
UPDATE shopping_system_product 
SET product_type_id = 1  -- 充氣床墊
WHERE 
  category = 'FJ' AND
  (name LIKE '%床%' OR name LIKE '%墊%' OR name LIKE '%氣墊%');

UPDATE shopping_system_product 
SET product_type_id = 8  -- 行李箱
WHERE 
  category = 'FJ' AND
  (name LIKE '%箱%' OR name LIKE '%旅行%' OR name LIKE '%行李%');

-- 4. Horizon 天際線品牌的特殊處理
UPDATE shopping_system_product 
SET product_type_id = 5  -- 登山背包
WHERE 
  category = 'Horizon 天際線' AND
  (name LIKE '%包%' OR name LIKE '%背包%');

UPDATE shopping_system_product 
SET product_type_id = 6  -- 登山杖
WHERE 
  category = 'Horizon 天際線' AND
  (name LIKE '%杖%' OR name LIKE '%登山杖%');

-- 處理品牌名稱變體問題
UPDATE shopping_system_product 
SET product_type_id = 3  -- 帳篷
WHERE 
  (category LIKE '%Coleman%' OR category LIKE '%科勒曼%' OR category LIKE '%高文%') AND
  product_type_id IS NULL;

UPDATE shopping_system_product 
SET product_type_id = 3  -- 帳篷
WHERE 
  (category LIKE '%Snow Peak%' OR category LIKE '%SNOW PEAK%' OR category LIKE '%SnowPeak%' OR category LIKE '%雪峰%') AND
  (name LIKE '%帳%' OR name LIKE '%營%') AND
  product_type_id IS NULL;

-- 處理名稱關鍵詞重疊問題
-- 對於同時包含多個類別關鍵詞的名稱，根據產品特性優先分類
UPDATE shopping_system_product 
SET product_type_id = 5  -- 優先識別為登山背包
WHERE 
  name LIKE '%登山背包%' AND
  (name LIKE '%睡墊%' OR name LIKE '%床墊%') AND
  product_type_id IS NULL;

UPDATE shopping_system_product 
SET product_type_id = 1  -- 優先識別為睡墊
WHERE 
  name LIKE '%睡墊%' AND
  name LIKE '%收納%' AND
  product_type_id IS NULL;

-- 清理未分類的產品 - 基於名稱的模糊匹配
UPDATE shopping_system_product 
SET product_type_id = 9  -- 瓦斯爐
WHERE 
  product_type_id IS NULL AND
  (name LIKE '%烹飪%' OR name LIKE '%烹調%' OR name LIKE '%火爐%' OR name LIKE '%煮食%');

UPDATE shopping_system_product 
SET product_type_id = 3  -- 帳篷
WHERE 
  product_type_id IS NULL AND
  (name LIKE '%戶外%' AND name LIKE '%遮陽%');

UPDATE shopping_system_product 
SET product_type_id = 5  -- 登山背包
WHERE 
  product_type_id IS NULL AND
  (name LIKE '%背負%' OR name LIKE '%揹%' OR name LIKE '%登山用%');

-- 基於描述的更詳細匹配
UPDATE shopping_system_product 
SET product_type_id = 3  -- 帳篷
WHERE 
  product_type_id IS NULL AND
  (description LIKE '%露營%' AND description LIKE '%防雨%' AND description LIKE '%戶外%');

-- 添加更多類別映射
UPDATE shopping_system_product 
SET product_type_id = 4  -- 充電器
WHERE 
  product_type_id IS NULL AND 
  (name LIKE '%充電%' OR name LIKE '%USB%' OR name LIKE '%電池%');

-- 最後，對常見露營品牌但未明確類別的產品進行處理
UPDATE shopping_system_product
SET product_type_id = 3  -- 假設大多數露營品牌未分類商品是帳篷類
WHERE 
  product_type_id IS NULL AND 
  (category IN ('Coleman', 'KAZMI', 'LIFECODE', 'ADISI', 'RHINO 犀牛'));

-- 顯示結果統計
SELECT 
  IFNULL(cd.category, '未分類') as category_name, 
  COUNT(*) as product_count 
FROM 
  shopping_system_product p
LEFT JOIN
  shopping_system_categorydisplay cd ON p.product_type_id = cd.id
GROUP BY 
  p.product_type_id
ORDER BY 
  product_count DESC;