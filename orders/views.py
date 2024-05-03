from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import User
from products.models import Product, Bidder, Bid
from django.views.generic import ListView
from django.contrib import messages

# 구매 - purchase
# @login_required
def purchase_history(request):
    # 로그인한 유저의 행만 가져오기
    products = Product.objects.filter(present_max_bidder_id = request.user.id) #present_max_bidder_id -> 임시적 필드
    # 진행 중인 상품의 개수 계산
    in_progress_count = products.filter(product_status=True).count()
    # 진행 중인 상품 목록 조회
    in_progress_sales = products.filter(product_status=True)
    # 종료된 상품의 개수 계산
    end_count = products.filter(product_status=False).count()
     # 종료된 상품 목록 조회
    completed_sales = products.filter(product_status=False)
    context = {
        'in_progress_sales': in_progress_sales,
        'completed_sales': completed_sales,
        'products' : products,
        'in_progress_count': in_progress_count,
        'end_count': end_count
    }
    return render(request, 'orders/purchase_history.html', context)


# @login_required
def purchase_history_ing_detail(request, pk):
    product = Product.objects.get(pk=pk)
    context = {
        'product' : product
    }
    return render(request, 'orders/purchase_history_ing_detail.html', context)

fin_bidder = None
# @login_required
def purchase_history_end_detail(request, pk):
    product = Product.objects.get(pk=pk)
    product_name = get_object_or_404(Product, pk=pk).name
    # bid 모델 변화 반영 후 수정 예정 (여기 부터)
    bid_list=list(Bid.objects.values())
    for bid in bid_list:
        if bid['product'] == product_name:
            global fin_bidder 
            fin_bidder = bid['bidder']
            return fin_bidder
    # 여기 까지
    user = request.user
    if fin_bidder == user:
        users_bid_result = '입찰에 성공하셨습니다.'
    else:
        users_bid_result = '입찰에 실패하셨습니다.'
    context = {
        'product' : product,
        'users_bid_result' : users_bid_result
    }
    return render(request, 'orders/purchase_history_end_detail.html', context)



# 판매 - Sales
# @login_required
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

# @login_required
def sales_history_ing(request):
    # 진행 중인 상품 목록 조회
    in_progress_sales = Product.objects.filter(seller=request.user, product_status=True)
    context = {
        'in_progress_sales': in_progress_sales
    }
    return render(request, 'orders/sales_history_ing.html', context)


# @login_required
def sales_history_end(request):
    # 종료된 상품 목록 조회
    completed_sales = Product.objects.filter(seller=request.user, product_status=False)
    context = {
        'completed_sales': completed_sales
    }
    return render(request, 'orders/sales_history_end.html', context)

# 입찰 참여
@login_required
def bid_participation(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        price_str = request.POST.get('price')
        
        # 가격 입력값이 비어있지 않은지 확인
        if price_str.strip():
            price = int(price_str)
            
            # present_max_bid_price가 None이면 min_bid_price를 사용
            current_max_bid = product.present_max_bid_price or product.min_bid_price

            if price > current_max_bid:
                if (price - current_max_bid) % product.bid_increment == 0:
                    product.present_max_bid_price = price
                    product.present_max_bidder_id = request.user.id
                    product.save()

                    # Bidder 인스턴스 생성 및 저장
                    bidder = Bidder(
                        product_id=product,  # 외래키 연결
                        bidder=request.user,  # 현재 로그인한 사용자
                        bid_price=price  # 입찰 가격
                    )
                    bidder.save()  # 데이터베이스에 저장
                    
                    messages.success(request, '성공적으로 입찰하였습니다.')
                else:
                    messages.error(request, f'입찰 금액은 {product.bid_increment}원 단위로 증가해야 합니다.')
            else:
                messages.error(request, '최소입찰가보다 더 높은 가격에 입찰하여야합니다.')
        else:
            messages.error(request, '유효한 입찰가를 입력해주세요.')

        return redirect('orders:purchase_history')
    
    context = {
        'product': product
    }
    return render(request, 'orders/bid_participation_form.html', context)



class ProductListView(ListView):
    model = Product
    template_name = 'orders/auction_page.html'
    context_object_name = 'products'
    paginate_by = 10  # 페이지네이션 적용할 경우

    def get_queryset(self):
        queryset = super().get_queryset()

        # 카테고리가 있는 경우에만 필터링
        category = self.kwargs.get('category')
        if category:
            queryset = queryset.filter(category=category)

        # 정렬 기능 추가
        sort_by = self.request.GET.get('sort')
        if sort_by == 'latest':
            queryset = queryset.order_by('-auction_start_time')
        elif sort_by == 'ending_soon':
            queryset = queryset.order_by('auction_end_time')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.kwargs.get('category', 'All')  # 카테고리가 없으면 'All'을 기본값으로 설정
        return context