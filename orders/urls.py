
from django.urls import path

from . import views

app_name = "orders"

#거래내역 ( 등록중 상품 목록, 입찰 참여중 상품 목록, 입찰 완료 상품 목록)
#(상품 등록) -> 등록중 상품 목록에 추가
#입찰 참여 - > 입찰가 입력 (-> 마일리지 차감) -> 입찰 참여중 목록에 올라감(product table 참조)
#입찰 완료 -> Bid 테이블에 새로운 행 생성 -> 입찰 완료 상품 목록에 추가 
urlpatterns = [
    path('purchase_history/', views.purchase_history, name='purchase_history'),
    path("purchase_history/ing/<int:pk>/", views.purchase_history_ing_detail, name="purchase_history_ing_detail"),
    path("purchase_history/end/<int:pk>/", views.purchase_history_end_detail, name="purchase_history_end_detail"),
    path('sales_history/', views.sales_history, name='sales_history'),
    path('sales_history/ing/<int:pk>/', views.sales_history_ing_detail, name='sales_history_ing_detail'),
    path('force-end-sales/<int:pk>/', views.force_end_sales, name='force_end_sales'),
    path('sales_history/end/<int:pk>/', views.sales_history_end_detail, name='sales_history_end_detail'),
    path('bid_participation/<int:pk>/', views.bid_participation, name='bid_participation'),
    path('payment/<int:pk>/', views.payment_page, name='payment_page'),
    path('payment_complete/', views.payment_complete, name='payment_complete'),
    path('auction/', views.ProductListView.as_view(), name='auction_page'),
    path('auction/<str:category>/', views.ProductListView.as_view(), name='auction_category_page'),
]