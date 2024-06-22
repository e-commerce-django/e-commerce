from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserActionViewSet, ProductViewSet, BidViewSet, UserViewSet, recommend_products

router = DefaultRouter()
router.register(r'useractions', UserActionViewSet)
router.register(r'product', ProductViewSet)
router.register(r'bid', BidViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('recommend/<int:user_id>/', recommend_products, name='recommend_products'),
]
