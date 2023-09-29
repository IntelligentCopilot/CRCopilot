from typing import List

from langchain.document_loaders import DirectoryLoader
from langchain.docstore.document import Document
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
import numpy as np
from FlagEmbedding import FlagModel
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct


collection_name = "knowledge_collection"
qdrant_url = "http://localhost:6333"
client = QdrantClient(qdrant_url)

folder_path = "./knowledges"


def get_embedding(text: List[str] | str) -> np.ndarray:

    model = FlagModel('BAAI/bge-large-zh-v1.5',
                      query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
                      use_fp16=False)

    return model.encode(text)


def load_knowledges(folder_path) -> List[Document]:
    print('loading knowledges')
    loader = DirectoryLoader(path=folder_path, glob="**/*.md", loader_cls=TextLoader, show_progress=True)
    docs = loader.load()
    text_spliter = CharacterTextSplitter(chunk_size=1024, chunk_overlap=128)
    split_docs = text_spliter.split_documents(docs)
    # print(split_docs[:2])
    # for doc in docs:
    #     print(doc)
    return split_docs


def add_embeddings():
    docs = load_knowledges(folder_path)
    points = []
    print('embedding, total: ', len(docs))
    for index, item in enumerate(docs):
        print(index+1)
        points.append(PointStruct(id=index, vector=get_embedding(
            item.page_content), payload=item.metadata))
    operation_info = client.upsert(
        collection_name=collection_name,
        wait=True,
        points=points
    )
    print(operation_info)


if __name__ == "__main__":
    # add embeddings
    add_embeddings()