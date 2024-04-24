from django.urls import path

from . import views

app_name = "orders"

#거래내역 ( 등록중 상품 목록, 입찰 참여중 상품 목록, 입찰 완료 상품 목록)
#(상품 등록) -> 등록중 상품 목록에 추가
#입찰 참여 - > 입찰가 입력 (-> 마일리지 차감) -> 입찰 참여중 목록에 올라감(product table 참조)
#입찰 완료 -> Bid 테이블에 새로운 행 생성 -> 입찰 완료 상품 목록에 추가 
urlpatterns = [
    # path("", views.MenuLV.as_view(), name="index"),
]