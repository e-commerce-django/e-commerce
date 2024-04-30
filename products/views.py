from django.shortcuts import render, redirect
from .forms import ProductForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic import ListView
from .models import Product

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_registrater.html'
    success_url = reverse_lazy('index') 

    def form_valid(self, form):
        form.instance.seller = self.request.user
        return super().form_valid(form)

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'