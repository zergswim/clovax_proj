# 설명자료
https://docs.google.com/presentation/d/1aaLObLDJnO8Ms1vcqV4MRQjvR3J1amsMp72lA1VCnTs/edit?usp=sharing

# CLOVA X API KEY 설정
./secret_ky.py 에 CLOAVA X 키설정 (API_KEY, API_KEY_PRIMAL_VAL, CLIENT_ID, CLIENT_SECRET)

# RAG 세팅
./vdb/docker-compose.yml 이용해서 milvus 구동 (docker-compose up -d)
./vdb/make_db.py 이용해서 Faust.txt 데이터 입력

# CLOVA X 구동
./main.py