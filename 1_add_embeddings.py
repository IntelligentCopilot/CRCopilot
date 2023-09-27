from typing import List

import numpy as np
from FlagEmbedding import FlagModel
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from utils.read_files import read_files_in_directory


collection_name = "knowledge_collection"
qdrant_url = "http://localhost:6333"
client = QdrantClient(qdrant_url)

folder_path = "./docs"


def get_embedding(text: List[str] | str) -> np.ndarray:

    model = FlagModel('BAAI/bge-large-zh-v1.5',
                      query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
                      use_fp16=False)

    return model.encode(text)


def add_embeddings():
    files = read_files_in_directory(folder_path)
    points = []

    for index, item in enumerate(files):
        points.append(PointStruct(id=index, vector=get_embedding(
            item["file_path"]), payload=item))

    operation_info = client.upsert(
        collection_name=collection_name,
        wait=True,
        points=points
    )

    print(operation_info)


if __name__ == "__main__":
    # add embeddings
    add_embeddings()
