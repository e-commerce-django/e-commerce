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
    product_status = models.BooleanField() # 상품이 현재 판매중이면 True 아니면 False
    category = models.CharField(max_length=30)
    size = models.IntegerField()
    present_max_bid_price = models.IntegerField(default=None, null=True) # 나중에 입력받기 때문에 null 허용
    present_max_bidder_id = models.IntegerField(default=None, null=True) # 나중에 입력받기 때문에 null 허용

    def save(self, *args, **kwargs):# product_status 필드의 값을 설정
        current_time = timezone.now()
        if self.auction_start_time <= current_time <= self.auction_end_time:
            self.product_status = True
        else:
            self.product_status = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'product'

class Bid(models.Model):
    bidder = models.ForeignKey(User, related_name='bids', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='bids', on_delete=models.CASCADE)
    bid_result = models.BooleanField()
    bid_price = models.IntegerField()
    bid_time = models.DateTimeField()

    # 변화된 코드가 반영이 안되는 오류 발생 -> 일단, 주석으로 처리
    # def __str__(self):
    #     return self.product

    def __repr__(self):
        return f"{self.bidder.name} - {self.bid_price}"

    class Meta:
        db_table = 'bid'


class Bidder(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bidder_product_id')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_price = models.DecimalField(max_digits=20, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)