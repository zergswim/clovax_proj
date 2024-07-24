#pip install pymilvus

import os
from vdb import embed

from pymilvus import (
    connections,
    FieldSchema, CollectionSchema, Collection,
    DataType,
    utility
)

def query(query, limit):
    # Milvus 연결 설정
    connections.connect(host="localhost", port="19530")
    embedding_dim = 1024
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=9000),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=embedding_dim)
    ]
    schema = CollectionSchema(fields, description="test")
    collection_name = "test"

    collection = Collection(name=collection_name, schema=schema, using='default', shards_num=2)
    query_vector = embed.embedding(query)

    search_params = {"metric_type": "IP", "params": {"ef": 64}}
    results = collection.search(
        data=[query_vector],  # 검색할 벡터 데이터
        anns_field="embedding",  # 검색을 수행할 벡터 필드 지정
        param=search_params,
        limit=limit,
        output_fields=["text"]
    )

    reference = []

    for hit in results[0]:
        distance = hit.distance
        text = hit.entity.get("text")
        reference.append({"distance": distance, "text": text})
        
    return text

if __name__ == '__main__':
    print(query("파우스트 작품의 마지막 부분에 대한 너의 생각을 알려줘", limit=1))