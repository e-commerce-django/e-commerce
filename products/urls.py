from django.contrib import admin
from django.urls import path
from products import views

urlpatterns = [
    path('registrater/', views.ProductCreateView.as_view(), name='product_registrater'),
]
