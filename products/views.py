from django.shortcuts import render, redirect
from .forms import ProductForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .models import Product

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_registrator.html'
    success_url = reverse_lazy('products:list') 