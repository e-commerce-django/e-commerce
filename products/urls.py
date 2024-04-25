from django.urls import path
from products import views

app_name = 'products'

urlpatterns = [
    path('registrater/', views.ProductCreateView.as_view(), name='product_registrater'),
    path('product_detail/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
]