from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import User
from products.models import Product, Bidder, Bid
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
    context = {
        'product' : product
    }
    return render(request, 'orders/purchase_history_ing_detail.html', context)

fin_bidder = None

def purchase_history_end_detail(request, pk):
    product = Product.objects.get(pk=pk)
    product_id = get_object_or_404(Product, pk=pk).id
    # bid 모델 변화 반영 후 수정 예정 (여기 부터)
    bid_list=list(Bid.objects.values())
    for bid in bid_list:
        if bid['product_id'] == product_id:
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
    return render(request, 'orders/bid_participation.html', context)


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
    
  

## 결제처리
## 결제 정보 인증 및 저장 -> 경매 종료일에 최고 입찰가에 한해 사용자 결제정보를 불러와 결제 처리

# a. 결제 정보 입력 및 저장
# 아임포트 토큰 발급 / 빌링키로 결제정보 저장 / 결제정보입력
def get_imp_token():      # 토큰 발급
    url = "https://api.iamport.kr/users/getToken"
    data = {
        'imp_key': settings.IAMPORT_API_KEY,
        'imp_secret': settings.IAMPORT_API_SECRET
    }
    response = requests.post(url, data=data)
    result = response.json()
    if result['code'] == 0:
        return result['response']['access_token']
    else:
        raise Exception("아임포트 토큰 발급 실패")
    
    
# 결제정보저장 by 빌링키결제 : 서비스 업체의 API를 호출하여 결제 정보를 저장하고, 이 과정에서 인증을 수행
def save_billing_key(customer_uid, card_number, expiry, birth, pwd_2digit): 
    token = get_imp_token()
    url = f"https://api.iamport.kr/subscribe/customers/{customer_uid}"
    headers = {
        'Authorization': token
    }
    data = {
        'card_number': card_number,
        'expiry': expiry,
        'birth': birth,
        'pwd_2digit': pwd_2digit
    }
    response = requests.post(url, headers=headers, data=data)
    result = response.json()
    if result['code'] == 0:
        return result['response']['customer_uid']
    else:
        raise Exception("빌링키 저장 실패")

from .forms import PaymentForm
@login_required
def process_payment(request):     # 결제정보 처리
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            product_id = form.cleaned_data['product_id']
            bid_amount = form.cleaned_data['bid_amount']
            card_number = form.cleaned_data['card_number']
            expiry = form.cleaned_data['expiry']
            birth = form.cleaned_data['birth']
            pwd_2digit = form.cleaned_data['pwd_2digit']

            product = get_object_or_404(Product, id=product_id)
            customer_uid = f"{request.user.id}_{product_id}"

            try:
                billing_key = save_billing_key(customer_uid, card_number, expiry, birth, pwd_2digit)
                bidder = Bidder.objects.create(
                    product_id=product,
                    bidder_id=request.user,
                    bid_price=bid_amount,
                    billing_key=billing_key
                )
                messages.success(request, '결제정보가 성공적으로 저장되었습니다.')
                return redirect('orders:bid_complete', product_id=product.id)
            except Exception as e:
                messages.error(request, str(e))
                return redirect('orders:bid_participation', pk=product.id)

    else:
        form = PaymentForm()

    return render(request, 'orders/process_payment.html', {'form': form})


def bid_complete(request, product_id):      # 입찰 완료 시, 문구
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'orders/bid_complete.html', {'product': product})


