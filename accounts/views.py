from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views.generic import View
from django.http import HttpResponse
from django.contrib import messages

class RegisterView(View):
    def get(self, request):
        return render(request, 'accounts/registration.html')


    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        if password != confirm_password:
            messages.error(request, '비밀번호가 일치하지 않습니다.')
            return redirect('/')

        # 회원 생성
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = name
        user.save()

        # 추가 필드 저장
        user_profile = user.profile
        user_profile.phone = phone
        user_profile.address = address
        user_profile.save()

        messages.success(request, '회원가입이 완료되었습니다. 로그인해주세요.')
        return redirect('login')

class LoginView(View):
    def get(self, request):
        return render(request, 'accounts/login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(username=email, password=password)

        if user is not None:
            login(request, user)
            return HttpResponse('로그인 성공')
        else:
            messages.error(request, '이메일 또는 비밀번호가 잘못되었습니다.')
            return redirect('/')
