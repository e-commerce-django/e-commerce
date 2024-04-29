from django.shortcuts import render
from products.models import Product

def index(request):
  object_list = Product.objects.all()
  context = {
     'object_list':object_list
  }
  return render(request, 'home.html', context)