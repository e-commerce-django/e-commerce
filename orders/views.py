from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from products.models import User, Product, Bid

@login_required
def purchase_history(request):
    # 로그인한 유저의 행만 가져오기
    products = Product.objects.filter(present_max_bidder_id = request.user.name) #present_max_bidder_id -> 임시적 필드
    # 진행 중인 상품의 개수 계산
    in_progress_count = products.filter(product_status=True).count()
    # 종료된 상품의 개수 계산
    end_count = products.filter(product_status=False).count()
    context = {
        'products' : products,
        'in_progress_count': in_progress_count,
        'end_count': end_count
    }
    return render(request, 'orders/purchase_history.html', context)

@login_required
def purchase_history_ing(request):
    # 로그인한 유저의 행만 가져오기
    products = Product.objects.filter(present_max_bidder_id = request.user.id) #present_max_bidder_id -> 임시적 필드
    # 진행 중인 상품 목록 조회
    in_progress_sales = products.filter(seller =request.user.name, product_status=True) # 괄호안 후에 수정 필수(user.name 관련)
    context = {
        'in_progress_sales': in_progress_sales
    }
    return render(request, 'orders/purchase_history_ing.html', context)

@login_required
def purchase_history_end(request):
    # 로그인한 유저의 행만 가져오기
    products = Product.objects.filter(present_max_bidder_id = request.user.id) #present_max_bidder_id -> 임시적 필드
    # 종료된 상품 목록 조회
    completed_sales = products.filter(seller=request.user.name, product_status=False) # 괄호안 후에 수정 필수(user.name 관련)
    context = {
        'completed_sales': completed_sales
    }
    return render(request, 'orders/purchase_history_end.html', context)