from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProductForm
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic import ListView
from .models import Product
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from api.models import UserAction


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_registrater.html'
    success_url = reverse_lazy('index') 

    def form_valid(self, form):
        form.instance.seller = self.request.user
        return super().form_valid(form)

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_time = timezone.now()
        context['auction_has_not_started'] = current_time < self.object.auction_start_time
        context['auction_has_ended'] = current_time > self.object.auction_end_time
        return context
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        
        if request.user.is_authenticated: # 로그인한 사용자의 경우에만 조회 기록 남김
            UserAction.objects.create(
                user=self.request.user,
                product=self.get_object(),
                action_type='view'
            )
        
        return response
    


# 좋아요 기능
@login_required
def product_like_toggle(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        if request.user in product.likes.all():
            product.likes.remove(request.user)
            # 좋아요 취소 시 UserAction 삭제
            UserAction.objects.filter(user=request.user, product=product, action_type='like').delete()
        else:
            product.likes.add(request.user)
            # 좋아요 기록
            UserAction.objects.create(
                user=request.user,
                product=product,
                action_type='like'
            )

    # next 파라미터로 리다이렉트 결정
    next_page = request.POST.get('next', reverse('products:product_detail', kwargs={'pk': pk}))
    return redirect(next_page)

@login_required
# 좋아요한 상품 목록 페이지
def liked_products(request):
    liked_products = Product.objects.filter(likes=request.user)
    return render(request, 'products/liked_products.html', {'liked_products': liked_products})