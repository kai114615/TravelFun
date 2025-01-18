from sentence_transformers import SentenceTransformer
import faiss

# 基本設定
model_name = 'sentence-transformers/distiluse-base-multilingual-cased-v1'
bi_encoder = SentenceTransformer(model_name)

# 讀取索引
index_path = './vector.index'
index = faiss.read_index(index_path)

# 查詢句子
list_query = ['位於古崗湖南側的獻台山上，為明魯王手書刻石遺跡之一，監國魯王為了反清復明，曾駐留金門島上逾10年，這方刻於明永曆6~8年（1652~1654）的勒石正表現他的慨然之氣，已列為縣定古蹟。']

# 將查詢句子轉換成向量
embeddings = bi_encoder.encode(
    list_query, 
    batch_size=4, 
    show_progress_bar=False,
    normalize_embeddings=False
)

# 查詢
D, I = index.search(embeddings, k=3)

# 顯示結果
list_scores = D.tolist()
list_ids = I.tolist()
print(f"相似度: {list_scores}")
print(f"檢索的 Document IDs 為: {list_ids}")

# 釋放記憶體
del index, embeddings