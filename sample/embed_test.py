import torch
from transformers import AutoTokenizer, AutoModel

# 사용할 모델과 토크나이저 로드
model_name = 'bert-base-uncased'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def embedding(input_text):
    input_ids = tokenizer.encode(input_text, return_tensors='pt')

    # 모델 계산
    with torch.no_grad():
        output = model(input_ids)


    # # 임베딩 추출
    # input_embedding = output.last_hidden_state[0]  # (seq_len, hidden_size)
    pooled_embedding = output.pooler_output  # (hidden_size,)

    # # print("output:", output)

    # # 임베딩 사용
    # # print("Input embedding shape:", input_embedding.shape)
    # # print("Pooled embedding shape:", pooled_embedding.shape)
    
    return pooled_embedding.tolist()[0]

# 입력 데이터 준비
# input_text = "한글 테스트"
# embedding(input_text)