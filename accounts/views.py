import os
import random
from dotenv import load_dotenv
load_dotenv()

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import View, TemplateView
from django.core.mail import send_mail, EmailMultiAlternatives
from .forms import UserForm, UserLoginForm, UserModifyForm
from products.models import Bid, Product
from .models import User
from api.models import UserRecommendations
from api.recommendation import get_recommendations
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse

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
                    recommendations = get_recommendations(user.id)
                    for recommendation in recommendations:
                        UserRecommendations.objects.create(
                            user_id=user.id,
                            product_id=recommendation.id,
                        )
                    return redirect('/')  
                else:
                    messages.error(request, '비밀번호가 일치하지 않습니다.')
            except User.DoesNotExist as e:
                messages.error(request, '존재하지 않는 이메일입니다.')
        return render(request, 'accounts/login.html', {'form': form})


class LogoutView(View):
    def get(self, request): 
        if request.user.is_authenticated:
            UserRecommendations.objects.filter(user_id=request.user.id).delete()
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
        

class EmailVerifyView(View):
    def get(self, request):
        return render(request, 'accounts/email_verify.html')

    def post(self, request):
        verification_code = request.POST.get('verification_code')
        session_verification_code = request.session.get('verification_code')

        if verification_code == session_verification_code:
            request.session['email_verified'] = True
            return redirect('register')
        else:
            messages.error(request, '인증 코드가 일치하지 않습니다.')
            return redirect('send_email')


def send_email(request):
    if request.method == "POST":
        verification_code = ''.join(random.choices('0123456789', k=6))
        request.session['verification_code'] = verification_code

        msg = EmailMultiAlternatives(
            "가입 인증 메일",
            f"{verification_code}",
            os.getenv("EMAIL_HOST_ID"),
            [request.POST.get("email")]
        )

        try:
            msg.send()
            return JsonResponse({'message': '이메일이 성공적으로 전송되었습니다.', 'verification_code': verification_code}, status=200) 
        except Exception as e:
            print(e)
            return JsonResponse({'error': '이메일 전송 중 오류가 발생했습니다.'}, status=400) 

        

@login_required
def withdraw(request):
    if request.method == 'POST':
        user = request.user
        if user.is_authenticated and user.is_active:
            user.is_active = False
            user.save()
            logout(request)
            return redirect('/')
        else:
            return redirect("withdraw/")
        
