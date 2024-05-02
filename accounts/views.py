from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, TemplateView

from .forms import UserForm, UserLoginForm, UserModifyForm

from products.models import Bid, Product
from .models import User


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/')  
        form = UserLoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        if request.user.is_authenticated:  
            return redirect('/')  
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, email=email, password=password)

                if user is not None:
                    login(request, user)
                    print("로그인 성공")
                    return redirect('/')  
                else:
                    print("비밀번호가 일치하지 않습니다.")
                    form.add_error('password', '비밀번호가 일치하지 않습니다.')
            except User.DoesNotExist as e:
                # print(e)
                form.add_error('email', '등록되지 않은 이메일입니다.')
        return render(request, 'accounts/login.html', {'form': form})


class LogoutView(View):
    def get(self, request): 
        if request.user.is_authenticated:
            logout(request)
            return redirect('/') 
        else:
            return redirect('/')  


class MyPageView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/mypage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 로그인한 사용자가 등록한 상품 내역 조회
        registered_products = Product.objects.filter(seller=self.request.user)
        context['registered_products'] = registered_products
        
        # 로그인한 사용자가 구매한 상품 내역 조회
        bought_products = Bid.objects.filter(bidder=self.request.user, bid_result=True)
        context['bought_products'] = bought_products
        
        return context


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:  
            return redirect('/')  
        form = UserForm()
        return render(request, 'accounts/registration.html', {'form': form})

    def post(self, request):
        if request.user.is_authenticated:  
            return redirect('/')  
        form = UserForm(request.POST)
        if form.is_valid():
            # 비밀번호를 해시하여 저장
            password = form.cleaned_data['password']
            hashed_password = make_password(password)
            print("password: ", password)
            print("hashed_password: ", hashed_password)
            
            user = User(
                email=form.cleaned_data['email'],
                password=hashed_password,
                username=form.cleaned_data['username'],
                address=form.cleaned_data['address'],
                phone_number=form.cleaned_data['phone_number'],
            )
            user.save()

            return redirect('/')  
        else:
            print("폼 유효성 검사 실패:", form.errors)
            return render(request, 'accounts/registration.html', {'form': form})


class ModifyView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        form = UserModifyForm(instance=user)

        return render(request, 'accounts/myinfo_modify.html', {'form': form})

    def post(self, request):
        user = request.user
        form = UserModifyForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('mypage')
        else:
            print("폼 유효성 검사 실패:", form.errors)
            return render(request, 'accounts/myinfo_modify.html', {'form': form})
        

@login_required
def withdraw(request):
    if request.method == 'POST':
        user = request.user
        if user.is_authenticated and user.is_active:
            user.is_active = False
            user.save()
            logout(request)
            # return JsonResponse({'message': '회원 탈퇴가 완료되었습니다.'}, status=200)
            return redirect('/')
        else:
            # return JsonResponse({'message': '오류가 발생했습니다.'}, status=400)
            return redirect("withdraw/")