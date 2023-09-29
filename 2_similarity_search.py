from typing import List

import numpy as np
from FlagEmbedding import FlagModel
from qdrant_client import QdrantClient


collection_name = "knowledge_collection"
qdrant_url = "http://localhost:6333"
client = QdrantClient(qdrant_url)


def get_embedding(text: List[str] | str) -> np.ndarray:

    flag_model = FlagModel('BAAI/bge-large-zh-v1.5',
                      query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
                      use_fp16=False)

    return flag_model.encode(text)


limit = 1
# threshold = 0.8


def query(text):
    query_vector = get_embedding(text)
    hits = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=limit,
    )
    context = ''
    for item in hits:
        context = item.payload['page_content']
        # print("Id:", item.id)
        # print("Version:", item.version)
        # print("Payload:", item.payload)
        print("Score:", item.score)
        print("Payload metadata:", item.payload['metadata'])
        print("---")  # 用于分隔每个字典
    return context


if __name__ == "__main__":
    query('''
          export default function Image() {
  return (
    <img
      src="https://i.imgur.com/ZF6s192.jpg"
      alt="'Floralis Genérica' by Eduardo Catalano: a gigantic metallic flower sculpture with reflective petals"
    />
  );
}
          ''')
