#pip install pymilvus

import embed
import sep
import os

from pymilvus import (
    connections,
    FieldSchema, CollectionSchema, Collection,
    DataType,
    utility
)

def make_collection():
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
    
    # 기존 컬렉션 삭제 (있다면)
    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)
        
    collection = Collection(name=collection_name, schema=schema, using='default', shards_num=2)

    # 문서 데이터 입력
    file_path = 'Faust.txt'
    documents = sep.split_paragraphs(file_path)

    # embedding_list = [[0.1] * 1024]  # Replace with actual 1024-dimensional float vector
    embedding_list = [embed.embedding(d) for d in documents]
    print("output embedding_dim:", len(embedding_list[0]))

    entities = [
        documents,
        embedding_list
    ]

    insert_result = collection.insert(entities)
    print("데이터 Insertion이 완료된 ID:", insert_result.primary_keys)
    print("데이터 Insertion이 전부 완료되었습니다")

    ##인덱스 생성 (옵션에 따라 검색속도 영향)
    index_params = {
        "metric_type": "IP",
        "index_type": "HNSW",
        "params": {
            "M": 8,
            "efConstruction": 200
        }
    }
    
    # collection = Collection(collection_name)
    collection.create_index(field_name="embedding", index_params=index_params)
    utility.index_building_progress(collection_name)
    
    print([index.params for index in collection.indexes])

    utility.load_state(collection_name)
    collection.load()
       
    return collection

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
    # 초기생성    
    make_collection()
    print(query("파우스트 작품의 마지막 부분에 대한 너의 생각을 알려줘", limit=1))