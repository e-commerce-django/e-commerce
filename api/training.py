import pandas as pd
from transformers import BertTokenizer, BertModel
import torch
import os
import numpy as np

class ProductDataset(torch.utils.data.Dataset):
    def __init__(self, texts, tokenizer, model):
        self.texts = texts
        self.tokenizer = tokenizer # BERT 토크나이저
        self.model = model # BERT 모델
 
    def __len__(self):
        return len(self.texts)

    def __getitem__(self, item): # 상품 텍스트 데이터 벡터화 및 학습 데이터 셋 변환
        text = self.texts[item]
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
        outputs = self.model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().detach().numpy()
        return {
            'text': text,
            'embedding': torch.tensor(embedding, dtype=torch.float, requires_grad=True)
        }

# 데이터 로드 및 전처리
products_df = pd.read_csv('products.csv')
user_actions_df = pd.read_csv('user_actions.csv')

tokenizer = BertTokenizer.from_pretrained('huawei-noah/TinyBERT_General_4L_312D')
model = BertModel.from_pretrained('huawei-noah/TinyBERT_General_4L_312D')

# 입력 데이터 생성 (labels는 dummy로)
texts = products_df['name'] + " " + products_df['description'] + " " + products_df['category'] + " " + products_df['tags'] + " " + products_df['size'].astype(str)

# 데이터셋 객체 생성
dataset = ProductDataset(texts=texts.tolist(), tokenizer=tokenizer, model=model)

# 모델 학습 설정
batch_size = 16 # 각 학습 반복에서 사용할 데이터 샘플의 수
learning_rate = 2e-5 # 학습률
epochs = 4 # 전체 데이터셋에 대해 학습을 반복할 횟수

train_dataloader = torch.utils.data.DataLoader( # 데이터 로더 설정(배치 크기, 데이터셋 정의)
    dataset,
    batch_size=batch_size,
    shuffle=True
)

optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate) # optimizer 설정(매개변수 최적화)
device = torch.device("cpu") # 학습 환경 설정 (cpu, gpu 등)
model.to(device)

for epoch in range(epochs): # 모델 학습 (에포크 수만큼 반복)
    model.train()
    for batch in train_dataloader:
        optimizer.zero_grad()
        inputs = tokenizer(batch['text'], return_tensors='pt', truncation=True, padding=True, max_length=512).to(device)
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze()
        optimizer.step()

    print(f"Epoch {epoch}")


# 모델 파라미터 저장
torch.save(model.state_dict(), 'bert_model.pth')
print("Model saved to bert_model.pth")