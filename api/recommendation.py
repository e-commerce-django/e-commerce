import os
import torch
import numpy as np
import hashlib
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
from .models import Product, UserAction, RecommendationResult
import json

class BERTEmbedding:
    def __init__(self):  # 저장된 BERT 모델 로드
        self.tokenizer = BertTokenizer.from_pretrained('huawei-noah/TinyBERT_General_4L_312D')
        self.model = BertModel.from_pretrained('huawei-noah/TinyBERT_General_4L_312D')
        self.model.load_state_dict(torch.load('bert_model.pth'))
        self.cache_dir = 'embedding_cache'

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_cache_path(self, text):  # 캐시 데이터 경로 설정
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return os.path.join(self.cache_dir, f'{text_hash}.npy')

    def encode(self, texts):  # 텍스트 데이터를 벡터화
        embeddings = []

        for text in texts:
            cache_path = self._get_cache_path(text)
            if os.path.exists(cache_path):  # 이미 있는 캐시데이터면 불러오기
                embedding = np.load(cache_path)
            else:  # 없다면 새로 임베딩 후 캐싱
                inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
                with torch.no_grad():
                    outputs = self.model(**inputs)
                embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
                np.save(cache_path, embedding)

            embeddings.append(embedding)

        return np.vstack(embeddings)

class RecommendationSystem:
    def __init__(self):
        self.embedder = BERTEmbedding()

    def get_product_embeddings(self, products):  # 상품 데이터를 입력받아 벡터화된 임베딩을 생성
        product_texts = [self._create_product_text(product) for product in products]
        if not product_texts:
            raise ValueError("The product texts list is empty!")
        embeddings = self.embedder.encode(product_texts)
        return list(zip([product.id for product in products], embeddings))

    def _create_product_text(self, product):  # 상품 데이터 text 생성
        return f"{product.name} {product.description} {product.category} {product.tags} {product.size}"

    def get_user_action_products(self, user_id):  # 특정 사용자의 행동 데이터를 바탕으로 관련 상품을 추출
        actions = UserAction.objects.filter(user_id=user_id).select_related('product')
        return [action.product for action in actions]

    def recommend(self, user_id, top_n=4):
        user_products = self.get_user_action_products(user_id)
        if not user_products:
            return []

        user_embeddings = self.get_product_embeddings(user_products)  # 사용자가 상호작용한 상품들 추출
        all_products = Product.objects.all()  # 모든 상품 데이터 추출
        all_product_embeddings = self.get_product_embeddings(all_products)

        user_embedding = sum([embedding for _, embedding in user_embeddings]) / len(user_embeddings)  # 사용자가 상호작용한 상품 임베딩의 평균을 계산(대표 벡터로 사용)

        similarities = self._calculate_similarities(user_embedding, all_product_embeddings)  # 계산된 사용자 벡터와 모든 판매 중인 상품의 벡터 사이의 유사도를 계산

        # 중복 제거 및 상태 필터링
        recommended_product_ids = list(dict.fromkeys([product_id for product_id, _ in similarities]))  # 중복 제거
        recommended_products = Product.objects.filter(id__in=recommended_product_ids, product_status=True)

        return recommended_products[:top_n]

    def _calculate_similarities(self, user_embedding, product_embeddings):
        similarities = []
        for product_id, embedding in product_embeddings:  # 각 상품의 벡터와 사용자 벡터 간의 유사도를 계산
            similarity = cosine_similarity([user_embedding], [embedding])[0][0]
            similarities.append((product_id, similarity))
        similarities.sort(key=lambda x: x[1], reverse=True)  # 튜플로 저장
        return similarities
    
    def save_recommendation_results(self, user_id, similarities, user_products, user_embeddings):
        for product_id, score in similarities:
            input_data = {
                "user_id": user_id,
                "user_embeddings": [embedding.tolist() for _, embedding in user_embeddings],
                "user_products": [product.id for product in user_products],
            }
            label_data = {
                "recommended_product_id": product_id,
                "score": float(score)  # float 형으로 변환
            }
            RecommendationResult.objects.create(
                user_id=user_id,
                product_id=product_id,
                score=score,
                action_type='recommend',  # 추천을 의미하는 새로운 액션 타입
                input_data=json.dumps(input_data, default=self._convert_to_serializable),
                label_data=json.dumps(label_data, default=self._convert_to_serializable)
            )

    def _convert_to_serializable(self, obj):  # float32 유형의 데이터를 직렬화
        if isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return obj

def get_recommendations(user_id):  # 사용자의 id를 받아 추천 목록 반환
    recommender = RecommendationSystem()
    return recommender.recommend(user_id)
