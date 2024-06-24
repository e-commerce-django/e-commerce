import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .models import Product, UserAction, RecommendationResult
import json

class BERTEmbedding:
    def __init__(self):
        self.cache_dir = 'embedding_cache'
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_cache_path(self, product_id):
        return os.path.join(self.cache_dir, f'product_{str(product_id)}.npy')

    def encode(self, product_ids):
        embeddings = []
        valid_product_ids = []
        for product_id in product_ids:
            cache_path = self._get_cache_path(product_id)
            if os.path.exists(cache_path):
                embedding = np.load(cache_path)
                embeddings.append(embedding)
                valid_product_ids.append(product_id)
            else:
                print(f'Embedding for product_id {product_id} not found in cache. Skipping.')
        if not embeddings:
            raise ValueError('No valid embeddings found in cache.')
        return np.vstack(embeddings), valid_product_ids

class RecommendationSystem:
    def __init__(self):
        self.embedder = BERTEmbedding()

    def get_product_embeddings(self, products):
        product_ids = [product.id for product in products]
        embeddings, valid_product_ids = self.embedder.encode(product_ids)
        return list(zip(valid_product_ids, embeddings))

    def get_user_action_products(self, user_id):
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
        action_weights = np.array(action_weights).reshape(-1, 1)

        # 가중합을 구하고 나누기
        weighted_user_embedding = (user_embeddings * action_weights).sum(axis=0) / action_weights.sum()

        all_products = Product.objects.all()
        all_product_embeddings_tuples = self.get_product_embeddings(all_products)

        similarities = self._calculate_similarities(weighted_user_embedding, all_product_embeddings_tuples)

        # 중복 제거 및 상태 필터링
        recommended_product_ids = list(dict.fromkeys([product_id for product_id, _ in similarities]))
        recommended_products = Product.objects.filter(id__in=recommended_product_ids, product_status=True)

        # 추천 결과 저장
        self.save_recommendation_results(user_id, similarities, user_products, user_embeddings)

        return recommended_products[:top_n]

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

def get_recommendations(user_id):
    recommender = RecommendationSystem()
    return recommender.recommend(user_id)
