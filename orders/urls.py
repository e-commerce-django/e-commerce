from django.urls import path

from . import views

app_name = "orders"

#거래내역 ( 등록중 상품 목록, 입찰 참여중 상품 목록, 입찰 완료 상품 목록)
#(상품 등록) -> 등록중 상품 목록에 추가
#입찰 참여 - > 입찰가 입력 (-> 마일리지 차감) -> 입찰 참여중 목록에 올라감(product table 참조)
#입찰 완료 -> Bid 테이블에 새로운 행 생성 -> 입찰 완료 상품 목록에 추가 
urlpatterns = [
    path('purchase_history/', views.purchase_history, name='purchase_history'),
    path("purchase_history/ing/", views.purchase_history_ing, name="purchase_history_ing"),
    path("purchase_history/end/", views.purchase_history_end, name="purchase_history_end"),
    path('sales_history/', views.sales_history, name='sales_history'),
    path('sales_history/ing/', views.sales_history_ing, name='sales_history_ing'),
    path('sales_history/end/', views.sales_history_end, name='sales_history_end'),
    path('bid_participation/<int:pk>/', views.bid_participation, name='bid_participation'),
    path('auction/', views.ProductListView.as_view(), name='auction_page'),
   path('auction/<str:category>/', views.ProductListView.as_view(), name='auction_category_page'),
]