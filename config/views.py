from django.db.models import Count
from django.shortcuts import render
from products.models import Product
from api.recommendation import get_recommendations
from api.models import UserRecommendations

def index(request):
    # 경매에 참여한 사람이 많은 상품 순으로 가져오기
    popular_products = Product.objects.annotate(num_bidders=Count('bidder_product_id')).filter(product_status=True).order_by('-num_bidders')[:3]
    sneakers = Product.objects.filter(category='스니커즈', product_status=True)
    athletic_shoes = Product.objects.filter(category='운동화', product_status=True)
    boots = Product.objects.filter(category='부츠', product_status=True)
    flats = Product.objects.filter(category='플랫슈즈', product_status=True)
    loafers = Product.objects.filter(category='로퍼', product_status=True)
    sandals = Product.objects.filter(category='샌들', product_status=True)
    slippers = Product.objects.filter(category='슬리퍼', product_status=True)

    # 추천 상품 가져오기
    if request.user.is_authenticated:
        recommended_products = UserRecommendations.objects.filter(user_id=request.user.id).select_related('product')
        recommended_products = [rec.product for rec in recommended_products]
    else:
        recommended_products = []

    context = {
        'recommended_products': recommended_products,
        'popular_products': popular_products,
        'sneakers': sneakers,
        'athletic_shoes': athletic_shoes,
        'boots': boots,
        'flats': flats,
        'loafers': loafers,
        'sandals': sandals,
        'slippers': slippers,
    }
    return render(request, 'home.html', context)