from django.db import models

class User(models.Model):
    email = models.EmailField(max_length=200, unique=True)
    password = models.TextField()
    name = models.CharField(max_length=40)
    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    user_type = models.BooleanField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'user'

class Product(models.Model):
    seller = models.ForeignKey(User, related_name='products', on_delete=models.CASCADE)
    name = models.TextField()
    description = models.TextField()
    image_url = models.TextField()
    min_bid_price = models.IntegerField()
    max_bid_price = models.IntegerField()
    bid_increment = models.IntegerField()
    auction_start_time = models.DateTimeField()
    auction_end_time = models.DateTimeField()
    product_status = models.BooleanField()
    present_max_bid_price = models.IntegerField()

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

    def __str__(self):
        return f"{self.bidder.name} - {self.bid_price}"

    class Meta:
        db_table = 'bid'
