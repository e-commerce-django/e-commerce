from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import User
from products.models import Product, Bidder, Bid
from api.models import UserAction
from django.views.generic import ListView
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
import requests
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
import logging
import os
import traceback
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
load_dotenv()

# 로거 설정
logger = logging.getLogger(__name__)

#구매 - purchase
def purchase_history(request):
    purchase_product_id_list = []
    # 로그인한 유저가 구입한 상품만 가져오기
    purchase_product_ids = Bidder.objects.filter(bidder_id=request.user.id)
    for purchase_product_id in purchase_product_ids:
        purchase_product_id_list.append(purchase_product_id.product_id)
    products = Product.objects.filter(name__in=purchase_product_id_list)
    # 진행 중인 상품의 개수 계산
    in_progress_count = products.filter(product_status=True).count()
    # 진행 중인 상품 목록 조회
    in_progress_sales = products.filter(product_status=True)
    # 종료된 상품의 개수 계산
    completed_count = products.filter(product_status=False).count()
     # 종료된 상품 목록 조회
    completed_sales = products.filter(product_status=False)
    context = {
        'in_progress_sales': in_progress_sales,
        'completed_sales': completed_sales,
        'products' : products,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count
    }
    return render(request, 'orders/purchase_history.html', context)

def purchase_history_ing_detail(request, pk):
    product = Product.objects.get(pk=pk)
    purchase_user = Bidder.objects.filter(product_id=pk, bidder_id=request.user.id).first()   # 사용자 희망 입찰가
    context = {
        'product' : product,
        'bid_price' : purchase_user.bid_price
    }
    return render(request, 'orders/purchase_history_ing_detail.html', context)



def purchase_history_end_detail(request, pk):
    product = Product.objects.get(pk=pk)

    fin_bid = Bid.objects.filter(product_id=pk).order_by('-bid_price').first()    # Bid 테이블에서의 해당 상품
    fin_bidder = fin_bid.bidder_id    # 해당 상품의 낙찰자 id

    current_user = request.user
    if fin_bidder == current_user.id:
        users_bid_result = '축하합니다! 경매에서 성공적으로 낙찰되었습니다.'
    else:
        users_bid_result = '이번에는 아쉽게도 낙찰되지 않았습니다. 다음 경매에서 더 나은 결과를 기대해 보세요!'
    context = {
        'product' : product,
        'users_bid_result' : users_bid_result
    }
    return render(request, 'orders/purchase_history_end_detail.html', context)


# 판매 - Sales
def sales_history(request):
    # 로그인한 유저의 행만 가져오기
    products = Product.objects.filter(seller_id=request.user.id)
    # 진행 중인 상품의 개수 계산
    in_progress_count = products.filter(product_status=True).count()
    # 진행 중인 상품 목록 조회
    in_progress_sales = products.filter(product_status=True)
    # 종료된 상품의 개수 계산
    completed_count = products.filter(product_status=False).count()
     # 종료된 상품 목록 조회
    completed_sales = products.filter(product_status=False)
    context = {
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'in_progress_sales': in_progress_sales,
        'completed_sales': completed_sales,
        'products' : products,
    }
    return render(request, 'orders/sales_history.html', context)


# 마이페이지 -> 판매 내역 -> 진행중 -> 하나의 상품의 상세페이지
def sales_history_ing_detail(request, pk):
    product = Product.objects.get(pk=pk)
    context = {
        'product' : product
    }
    return render(request, 'orders/sales_history_ing_detail.html', context)

# 강제 판매 종료 처리
def force_end_sales(request, pk):
    # 해당 상품 및 입찰 결과 가져오기
    product = get_object_or_404(Product, pk=pk)
    bids = Bid.objects.filter(product=product)

    # 강제 판매 종료 버튼을 눌렀을 때 필드값 변경
    if request.method == 'POST':
        product.product_status = False
        product.auction_end_time = timezone.now()
        product.present_max_bidder_price = 0
        product.present_max_bidder_id = 0
        product.save()

        # 각각의 입찰 결과를 수정하고 저장
        for bid in bids:
            bid.bid_result = False
            bid.bid_time = timezone.now()
            bid.save()

    return redirect('orders:sales_history_ing_detail', pk=pk)

# 마이페이지 -> 판매 내역 -> 진행 종료 -> 하나의 상품의 상세페이지
def sales_history_end_detail(request, pk):
    product = Product.objects.get(pk=pk)
    bid = Bid.objects.filter(product=product)

    context = {
        'product' : product,
        'bid' : bid,
    }
    return render(request, 'orders/sales_history_end_detail.html', context)


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
                        bidder_id=request.user,  # 현재 로그인한 사용자
                        bid_price=price  # 입찰 가격
                    )
                    bidder.save()  # 데이터베이스에 저장

                    # 입찰 기록
                    UserAction.objects.create(
                        user=request.user,
                        product=product,
                        action_type='bid'
                    )
                    
                    messages.success(request, '성공적으로 입찰하였습니다.')
                    return redirect('orders:payment_page', pk=product.pk)   # 결제 페이지로
                else:
                    messages.error(request, f'입찰 금액은 {product.bid_increment}원 단위로 증가해야 합니다.')
            else:
                messages.error(request, '최소입찰가보다 더 높은 가격에 입찰하여야합니다.')
        else:
            messages.error(request, '유효한 입찰가를 입력해주세요.')
    
    context = {
        'product': product
    }
    return render(request, 'orders/bid_participation.html', context)


@login_required
def payment_page(request, pk):
    product = get_object_or_404(Product, pk=pk)
    context = {
        'product': product
    }
    return render(request, 'orders/payment_page.html', context)


@login_required
def payment_complete(request):
    return render(request, 'orders/payment_complete.html')



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

        return queryset.filter(product_status=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.kwargs.get('category', 'All')  # 카테고리가 없으면 'All'을 기본값으로 설정
        return context
    