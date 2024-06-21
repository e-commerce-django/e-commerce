from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import UserAction
from rest_framework import viewsets
from products.models import Product
from products.models import Bid
from accounts.models import User
from .recommendation import get_recommendations
from .serializers import ProductSerializer, BidSerializer, UserSerializer, UserActionSerializer

@api_view(['GET'])
def recommend_products(request, user_id):
    recommendations = get_recommendations(user_id)
    serializer = ProductSerializer(recommendations, many=True)
    return Response(serializer.data)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserActionViewSet(viewsets.ModelViewSet):
    queryset = UserAction.objects.all()
    serializer_class = UserActionSerializer