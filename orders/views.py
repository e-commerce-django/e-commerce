from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import User
from products.models import Product, Bid

# 구매 - purchase
# @login_required
def purchase_history(request):
    # 로그인한 유저의 행만 가져오기
    products = Product.objects.filter(present_max_bidder_id = request.user.id) #present_max_bidder_id -> 임시적 필드
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

# @login_required
def purchase_history_ing(request):
    # 로그인한 유저의 행만 가져오기
    products = Product.objects.filter(present_max_bidder_id = request.user.id) #present_max_bidder_id -> 임시적 필드
    # 진행 중인 상품 목록 조회
    in_progress_sales = products.filter(product_status=True) # 괄호안 후에 수정 필수(user.name 관련)
    context = {
        'in_progress_sales': in_progress_sales
    }
    return render(request, 'orders/purchase_history_ing.html', context)

# @login_required
def purchase_history_end(request):
    # 로그인한 유저의 행만 가져오기
    products = Product.objects.filter(present_max_bidder_id = request.user.id) #present_max_bidder_id -> 임시적 필드
    # 종료된 상품 목록 조회
    completed_sales = products.filter(product_status=False) # 괄호안 후에 수정 필수(user.name 관련)
    context = {
        'completed_sales': completed_sales
    }
    return render(request, 'orders/purchase_history_end.html', context)



# 판매 - Sales
@login_required
def sales_history(request):
    # 진행 중인 상품의 개수 계산
    in_progress_count = Product.objects.filter(seller=request.user, product_status=True).count()
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

# 입찰 참여
# @login_required
def bid_participation(request, pk):
    # get
    if request.method=='GET':
        product = Product.objects.filter(id=pk)
        context = {
        'product': product
        }
        return render(request, 'orders/bid_participation_form.html', context)
    # post
    elif request.method=="POST":
        # 폼에서 전달되는 각 값을 뽑아와서 DB에 저장
        user = request.user
        seller = request.POST['seller']
        product = request.POST['product']
        price = request.POST['price']
        
        # product 테이블의 present_max_bid_price과 present_max_bidder_id 값 갱신
        new_bider = Product.objects.get(seller = seller, name = product)
        new_bider(present_max_bid_price = price, present_max_bidder_id = user)
        new_bider.save()    

    return redirect('orders:purchase_history')