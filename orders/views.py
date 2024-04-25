from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from products.models import User, Product, Bid

def sales_history(request):
    # 진행 중인 상품의 개수 계산
    in_progress_count = Product.objects.filter(product_status=True).count()
    # 종료된 상품의 개수 계산
    end_count = Product.objects.filter(product_status=False).count()
    context = {
        'in_progress_count': in_progress_count,
        'end_count': end_count
    }
    return render(request, 'orders/sales_history.html', context)


def sales_history_ing(request):
    # 진행 중인 상품 목록 조회
    in_progress_sales = Product.objects.filter(seller_id=request.user.id, product_status=True)
    context = {
        'in_progress_sales': in_progress_sales
    }
    return render(request, 'orders/sales_history_ing.html', context)



def sales_history_end(request):
    # 종료된 상품 목록 조회
    completed_sales = Product.objects.filter(seller_id=request.user.id, product_status=False)
    context = {
        'completed_sales': completed_sales
    }
    return render(request, 'orders/sales_history_end.html', context)


class PurchaseHisIngLV(ListView):
    pass

class PurchaseHisEndLV(ListView):
    pass