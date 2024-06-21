from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import torch
from .models import Product, UserAction

class BERTEmbedding:
    def __init__(self): # 저장된 BERT 모델 로드
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased')
        self.model.load_state_dict(torch.load('bert_model.pth'))

    def encode(self, texts): # 텍스트 데이터를 벡터화
        if not texts:
            raise ValueError("The input text list is empty!")
        inputs = self.tokenizer(texts, return_tensors='pt', truncation=True, padding=True, max_length=512)
        outputs = self.model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).detach().numpy()
        return embeddings

class RecommendationSystem:
    def __init__(self):
        self.embedder = BERTEmbedding()

    def get_product_embeddings(self, products): # 상품 데이터를 입력받아 벡터화된 임베딩을 생성
        product_texts = [self._create_product_text(product) for product in products]
        if not product_texts:
            raise ValueError("The product texts list is empty!")
        embeddings = self.embedder.encode(product_texts)
        return list(zip([product.id for product in products], embeddings))

    def _create_product_text(self, product): # 상품 데이터 text 생성
        return f"{product.name} {product.description} {product.category} {product.tags} {product.size}"

    def get_user_action_products(self, user_id): # 특정 사용자의 행동 데이터를 바탕으로 관련 상품을 추출
        actions = UserAction.objects.filter(user_id=user_id).select_related('product')
        return [action.product for action in actions]

    def recommend(self, user_id, top_n=4):
        user_products = self.get_user_action_products(user_id)
        if not user_products:
            return []

        user_embeddings = self.get_product_embeddings(user_products) # 사용자가 상호작용한 상품들 추출
        all_products = Product.objects.all() # 모든 상품 데이터 추출
        all_product_embeddings = self.get_product_embeddings(all_products)

        user_embedding = sum([embedding for _, embedding in user_embeddings]) / len(user_embeddings) # 사용자가 상호작용한 상품 임베딩의 평균을 계산(대표 벡터로 사용)

        similarities = self._calculate_similarities(user_embedding, all_product_embeddings) # 계산된 사용자 벡터와 모든 판매 중인 상품의 벡터 사이의 유사도를 계산

        # 중복 제거 및 상태 필터링
        recommended_product_ids = list(dict.fromkeys([product_id for product_id, _ in similarities])) # 중복 제거
        recommended_products = Product.objects.filter(id__in=recommended_product_ids, product_status=True)

        return recommended_products[:top_n]

    def _calculate_similarities(self, user_embedding, product_embeddings):
        similarities = []
        for product_id, embedding in product_embeddings: # 각 상품의 벡터와 사용자 벡터 간의 유사도를 계산
            similarity = cosine_similarity([user_embedding], [embedding])[0][0]
            similarities.append((product_id, similarity))
        similarities.sort(key=lambda x: x[1], reverse=True) # 튜플로 저장
        return similarities

def get_recommendations(user_id): # 사용자의 id를 받아 추천 목록 반환
    recommender = RecommendationSystem()
    return recommender.recommend(user_id)
