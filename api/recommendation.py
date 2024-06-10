import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
from products.models import Product

def get_recommendations(product_id, top_n=4):
    # 모든 상품을 데이터프레임으로 변환
    products = Product.objects.all().values('id', 'name', 'category', 'size', 'tags')
    df = pd.DataFrame(products)
    
    #카테고리와 사이즈를 태그 리스트에 추가
    df['tags'] = df.apply(lambda x: x['tags'] + [x['category']] + [str(x['size'])], axis=1)

    # 태그 데이터를 이진 인코딩
    mlb = MultiLabelBinarizer()
    tags_encoded = mlb.fit_transform(df['tags'])
    
    # 코사인 유사도 계산
    cosine_sim = cosine_similarity(tags_encoded)
    
    # 입력 상품의 인덱스를 찾음
    idx = df.index[df['id'] == product_id].tolist()[0]
    
    # 모든 상품과의 유사도 점수를 계산하고 정렬
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # 가장 유사한 top_n 상품을 반환 (자기 자신 제외)
    sim_scores = sim_scores[1:top_n+1]
    product_indices = [i[0] for i in sim_scores]
    
    return df.iloc[product_indices]