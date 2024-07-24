#pip install pymilvus transformers torch sentence-transformers

import os
from pymilvus import (
    connections,
    FieldSchema, CollectionSchema, Collection,
    DataType,
    utility
)
from transformers import RagTokenizer, RagSequenceForGeneration
from sentence_transformers import SentenceTransformer
# import torch

# Milvus 연결 설정
connections.connect(host="localhost", port="19530")

# Milvus 컬렉션 및 필드 스키마 설정
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=10240),
    # FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768)
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384)
]
schema = CollectionSchema(fields=fields, description="Document collection")
collection_name = "document_collection"

# 기존 컬렉션 삭제 (있다면)
if utility.has_collection(collection_name):
    utility.drop_collection(collection_name)

# 새 컬렉션 생성
collection = Collection(collection_name, schema)

# 문서 임베딩을 위한 모델 로드 (384-dimensional embeddings)
sentence_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# 문서 데이터 입력
documents = [
    "This is the first document.",
    "The second document is about a different topic.",
    "The third document provides additional information.",
]

# 문서 임베딩 및 Milvus에 삽입
embeddings = sentence_model.encode(documents)
print("Embeddings shape:", embeddings.shape)

# collection.insert([documents, embeddings.tolist()])
for doc, emb in zip(documents, embeddings.tolist()):
    collection.insert([
        [doc],  # text field
        [emb]   # embedding field
    ])

# 인덱스 생성
index_params = {
    "index_type": "IVF_FLAT",
    "metric_type": "L2",
    # "params": {"nlist": 128}
    "params": {"nlist": 64}  # Reduced from 128
}
collection.create_index("embedding", index_params)
collection.load()

# RAG 모델 및 토크나이저 초기화
rag_tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")
rag_model = RagSequenceForGeneration.from_pretrained("facebook/rag-token-nq")

# Milvus를 사용한 검색 함수
def search_milvus(query, top_k=1):
    query_embedding = sentence_model.encode([query])[0]
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    results = collection.search(
        data=[query_embedding.tolist()],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        output_fields=["text"]
    )
    return [hit.entity.get('text') for hit in results[0]]

# RAG 모델을 사용하여 질문에 대한 답변 생성
question = "What is the topic of the second document?"
retrieved_docs = search_milvus(question)

input_ids = rag_tokenizer(question, return_tensors="pt").input_ids
context_input_ids = rag_tokenizer(retrieved_docs, return_tensors="pt", padding=True, truncation=True).input_ids

rag_model.config.use_dummy_dataset = True
rag_model.config.label_smoothing = 0.1
rag_model.config.title_sep = " "

generator = rag_model.generate(
    input_ids,
    context_input_ids=context_input_ids,
    num_return_sequences=1,
    num_beams=4,
    early_stopping=True,
    max_length=100
)

answer = rag_tokenizer.decode(generator[0], skip_special_tokens=True)
print(f"Question: {question}")
print(f"Answer: {answer}")

# 작업 완료 후 컬렉션 해제 및 연결 종료
collection.release()
connections.disconnect("default")