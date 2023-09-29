from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams


collection_name = "knowledge_collection"

qdrant_url = "http://localhost:6333"

dimension = 1024

client = QdrantClient(qdrant_url)


if __name__ == "__main__":
    # create collection
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
    )


# 浏览器访问 
# http://localhost:6333/collections
# {"result":{"collections":[{"name":"knowledge_collection"}]},"status":"ok","time":0.000047334}

# 删除 collection
# curl -L -X DELETE 'http://localhost:6333/collections/knowledge_collection' \
# -H 'Content-Type: application/json' \
# --data-raw '{
# }'

