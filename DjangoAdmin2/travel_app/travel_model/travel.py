import pymysql
import os
from sentence_transformers import SentenceTransformer
import faiss

# 資料庫連線
connection = pymysql.connect(
    host = 'localhost',
    user = 'root',
    password = 'P@ssw0rd',
    database = 'travel_app',
    charset = 'utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# 取得 cursor 物件，進行 CRUD
cursor = connection.cursor()

try:
    # 模型名稱
    model_name = 'sentence-transformers/distiluse-base-multilingual-cased-v1'

    # 索引存放路徑
    index_path = './vector.index'

    # 讀取 model
    bi_encoder = SentenceTransformer(model_name)

    # 寫入資料
    # sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
    # cursor.execute(sql, ('webmaster@python.org', 'very-secret'))

    # 查詢資料
    sql = "SELECT * FROM travel_app.travel WHERE travel_id BETWEEN 1 AND 5084"
    cursor.execute(sql)

    # 查詢結果列數大於0 ，代表有資料
    if cursor.rowcount > 0:
        # 將查詢結果轉成 list 型態 (裡頭元素都是 dict)
        objects = cursor.fetchall() # 如果 sql 語法明顯只取得一筆，則使用 fetchone()

        # 
        id = []

        # 
        travel_txt = []

        # 迭代取得資料 (dict 型態)
        for obj in objects:
            id.append(int(obj['travel_id']))
            travel_txt.append(obj['travel_txt'])

        # 將所有句子轉換成向量，同時計算轉向量時間
        embeddings = bi_encoder.encode(
            travel_txt, 
            batch_size=512,
            show_progress_bar=True,
            normalize_embeddings=False # 建議先查詢預訓練模型是否支援
        )

        # 讀取索引，不存在就初始化
        if not os.path.exists(index_path):
            dims = embeddings.shape[1]
            index = faiss.IndexFlatIP(dims) # 初始化索引的維度
            index = faiss.IndexIDMap(index) # 讓 index 有記錄對應 doc id 的能力
        else:
            # 索引存在，直接讀取
            index = faiss.read_index(index_path)

        # 加入 doc id 到 對應的 vector
        index.add_with_ids(embeddings, id) # 加入 向量 與 文件ID
        # index.add(embeddings) # 僅加入向量

        # 儲存索引
        faiss.write_index(index, index_path)

        # 釋放記憶體
        del index, embeddings
    else:
        print("rowcount: 0")

    # 提交 SQL 執行結果
    # connection.commit()

    
except Exception as e:
    # 回滾
    connection.rollback()
    print("SQL 執行失敗")
    print(e)



# 釋放 cursor
cursor.close()

# 關閉資料庫連線
connection.close()
