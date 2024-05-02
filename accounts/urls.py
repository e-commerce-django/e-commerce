from django.urls import path
from .views import RegisterView, LoginView, MyPageView, LogoutView, ModifyView, withdraw


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("mypage/", MyPageView.as_view(), name="mypage"),
    path('mypage/myinfo_modify/', ModifyView.as_view(), name="myinfo_modify"),
    path("mypage/withdraw/", withdraw, name="withdraw"),
]
