from django.db import models
from accounts.models import User
from products.models import Product
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from products.models import Product  # Product 모델이 다른 앱에 있는 경우

class UserAction(models.Model):
    ACTION_TYPES = (
        ('view', 'View'),
        ('like', 'Like'),
        ('bid', 'Bid'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.action_type}"
    
    class Meta:
        db_table = "useraction"

class UserRecommendations(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

class RecommendationResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    score = models.FloatField()
    action_type = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)
    input_data = models.JSONField()  # 입력 데이터
    label_data = models.JSONField()  # 레이블 데이터