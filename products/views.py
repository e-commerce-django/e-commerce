from django.shortcuts import render, redirect
from .forms import ProductForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from .models import Product

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_registrater.html'
    success_url = reverse_lazy('products:list') 

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
