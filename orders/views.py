from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from products.models import User, Product, Bid
from django.views.generic import ListView


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



# 판매 - Sales
@login_required
def sales_history(request):
    # 진행 중인 상품의 개수 계산
    in_progress_count = Product.objects.filter(seller=request.user, product_status=True).count()      # seller -> seller_id???
    # 종료된 상품의 개수 계산
    end_count = Product.objects.filter(seller=request.user, product_status=False).count()
    context = {
        'in_progress_count': in_progress_count,
        'end_count': end_count
    }
    return render(request, 'orders/sales_history.html', context)

@login_required
def sales_history_ing(request):
    # 진행 중인 상품 목록 조회
    in_progress_sales = Product.objects.filter(seller=request.user, product_status=True)
    context = {
        'in_progress_sales': in_progress_sales
    }
    return render(request, 'orders/sales_history_ing.html', context)


@login_required
def sales_history_end(request):
    # 종료된 상품 목록 조회
    completed_sales = Product.objects.filter(seller=request.user, product_status=False)
    context = {
        'completed_sales': completed_sales
    }
    return render(request, 'orders/sales_history_end.html', context)



class ProductListView(ListView):
    model = Product
    template_name = 'orders/auction_page.html'
    context_object_name = 'products'
    paginate_by = 10  # 페이지네이션 적용할 경우



def auction_catetory(request, category=None):
    # 모든 상품을 가져오는 기본 쿼리셋
    products = Product.objects.all()

    # 카테고리가 지정되었다면 해당 카테고리의 상품만 필터링
    if category:
        products = products.filter(category=category)

    context = {
        'products': products
    }
    return render(request, 'orders/auction_page.html', context)