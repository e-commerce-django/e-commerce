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
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased')
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
        user_products = [(action.product, self._get_action_weight(action.action_type)) for action in actions]
        return user_products

    def _get_action_weight(self, action_type):
        if action_type == 'bid':
            return 10
        elif action_type == 'like':
            return 3
        elif action_type == 'view':
            return 1
        else:
            return 0

    def recommend(self, user_id, top_n=4):
        user_actions = self.get_user_action_products(user_id)
        if not user_actions:
            return []

        user_products, action_weights = zip(*user_actions)
        user_embeddings_tuples = self.get_product_embeddings(user_products)

        # user_embeddings에서 임베딩을 추출하여 numpy 배열로 변환
        user_embeddings = np.array([embedding for _, embedding in user_embeddings_tuples])
        action_weights = np.array(action_weights).reshape(-1, 1)  # action_weights의 차원을 맞추기 위해 reshape

        # 가중합을 구하고 나누기
        weighted_user_embedding = (user_embeddings * action_weights).sum(axis=0) / action_weights.sum()

        all_products = Product.objects.all()
        all_product_embeddings_tuples = self.get_product_embeddings(all_products)

        similarities = self._calculate_similarities(weighted_user_embedding, all_product_embeddings_tuples)

        # 중복 제거 및 상태 필터링
        recommended_product_ids = []
        seen_product_ids = set()

        for product_id, _ in similarities:
            if product_id not in seen_product_ids:
                recommended_product_ids.append(product_id)
                seen_product_ids.add(product_id)
                if len(recommended_product_ids) == top_n:
                    break

        recommended_products = Product.objects.filter(id__in=recommended_product_ids, product_status=True)

        # 추천 결과 저장
        self.save_recommendation_results(user_id, similarities, user_products, user_embeddings)

        return recommended_products

    def _calculate_similarities(self, user_embedding, product_embeddings):
        similarities = [(product_id, cosine_similarity([user_embedding], [embedding])[0][0]) for product_id, embedding in product_embeddings]
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities

    def save_recommendation_results(self, user_id, similarities, user_products, user_embeddings):
        for product_id, score in similarities:
            input_data = {
                "user_id": user_id,
                "user_embeddings": [embedding.tolist() for embedding in user_embeddings],
                "user_products": [product.id for product in user_products],
            }
            label_data = {
                "recommended_product_id": product_id,
                "score": float(score)
            }
            RecommendationResult.objects.create(
                user_id=user_id,
                product_id=product_id,
                score=score,
                action_type='recommend',
                input_data=json.dumps(input_data, default=self._convert_to_serializable),
                label_data=json.dumps(label_data, default=self._convert_to_serializable)
            )

    def _convert_to_serializable(self, obj):
        if isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return obj

def get_recommendations(user_id):  # 사용자의 id를 받아 추천 목록 반환
    recommender = RecommendationSystem()
    return recommender.recommend(user_id)
