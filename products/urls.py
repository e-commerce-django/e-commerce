from django.urls import path
from products import views

app_name = 'products'

urlpatterns = [
    path('registrater/', views.ProductCreateView.as_view(), name='product_registrater'),
    path('product_detail/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:pk>/like-toggle/', views.product_like_toggle, name='product_like_toggle'),
    path('liked-products/', views.liked_products, name='liked_products'),
]