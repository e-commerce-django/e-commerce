from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from accounts.models import User
from django.conf import settings

class Product(models.Model):
    seller = models.ForeignKey(User, related_name='products', on_delete=models.CASCADE, db_column='seller_id')
    name = models.CharField(max_length=100)
    description = models.TextField()
    image_url = models.TextField()
    min_bid_price = models.IntegerField()
    bid_increment = models.IntegerField()
    auction_start_time = models.DateTimeField()
    auction_end_time = models.DateTimeField()
    product_status = models.BooleanField(default=False) # 상품이 현재 판매중이면 True 아니면 False
    category = models.CharField(max_length=30)
    size = models.IntegerField()
    present_max_bid_price = models.IntegerField(default=None, null=True) # 나중에 입력받기 때문에 null 허용
    present_max_bidder_id = models.IntegerField(default=None, null=True) # 나중에 입력받기 때문에 null 허용
    likes = models.ManyToManyField(User, related_name='liked_products', blank=True)   # 해당 상품에 좋아요한 사용자 집합 필드 추가

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'product'

class Bid(models.Model):
    bidder = models.ForeignKey(User, related_name='bids', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, related_name='bids', on_delete=models.CASCADE)
    bid_result = models.BooleanField()
    bid_price = models.IntegerField(null=True, blank=True)
    bid_time = models.DateTimeField()

    def __str__(self):
        if self.bidder:
            return f"{self.bidder.username} - {self.bid_price}"
        else:
            return "No bidder - " + str(self.bid_price)


    class Meta:
        db_table = 'bid'


class Bidder(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bidder_product_id')
    bidder_id = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_price = models.DecimalField(max_digits=20, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)
    billing_key = models.CharField(max_length=255, blank=True)  # 빌링키 저장 필드