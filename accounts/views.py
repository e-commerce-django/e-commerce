from django.shortcuts import render, redirect
from products.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.http import HttpResponse
from django.contrib import messages
from .forms import UserForm, UserLoginForm
from django.contrib.auth.hashers import make_password, check_password


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:  # 이미 로그인된 경우
            return redirect('/')  # 루트 URL로 리다이렉션
        form = UserForm()
        return render(request, 'accounts/registration.html', {'form': form})

    def post(self, request):
        if request.user.is_authenticated:  # 이미 로그인된 경우
            return redirect('/')  # 루트 URL로 리다이렉션
        form = UserForm(request.POST)
        if form.is_valid():
            # 비밀번호를 해시하여 저장
            password = form.cleaned_data['password']
            hashed_password = make_password(password)
            print("password: ", password)
            print("hashed_password: ", hashed_password)
            
            # 새로운 사용자 생성
            user = User(
                email=form.cleaned_data['email'],
                password=hashed_password,
                username=form.cleaned_data['username'],
                address=form.cleaned_data['address'],
                phone_number=form.cleaned_data['phone_number'],
            )
            user.save()

            # 회원가입 성공 후, 로그인 페이지로 이동하거나 다른 페이지로 리다이렉트
            return redirect('/')  # 로그인 페이지로 이동하도록 설정 (login은 로그인 URL의 이름입니다)
        else:
            print("폼 유효성 검사 실패:", form.errors)
            return render(request, 'accounts/registration.html', {'form': form})

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/')  # 이미 로그인된 경우 루트 페이지로 리다이렉션
        form = UserLoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        if request.user.is_authenticated:  # 이미 로그인된 경우
            return redirect('/')  # 루트 URL로 리다이렉션
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(email=email)
                # 인증
                user = authenticate(request, email=email, password=password)
                if user is not None:
                    # 인증에 성공하면 로그인
                    login(request, user)
                    print("로그인 성공")
                    return redirect('/')  # 로그인 후 리다이렉트할 URL
                else:
                    # 인증에 실패하면 에러메시지 표시
                    print("비밀번호가 일치하지 않습니다.")
                    form.add_error('password', '비밀번호가 일치하지 않습니다.')
            except User.DoesNotExist as e:
                # 해당 이메일로 등록된 사용자가 없는 경우
                print(e)
                form.add_error('email', '등록되지 않은 이메일입니다.')
        return render(request, 'accounts/login.html', {'form': form})
