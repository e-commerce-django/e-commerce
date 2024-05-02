from django.contrib import admin
from django.db import models
from .models import Product, Bid, Bidder
from accounts.models import User
from django.forms import IntegerField, TextInput

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone_number', 'user_type']
    search_fields = ['username', 'email']
    list_filter = ['user_type']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = ['id', 'seller', 'name', 'description', 'image_url', 'min_bid_price', 'bid_increment', 'auction_start_time', 'auction_end_time', 'product_status', 'present_max_bid_price', 'present_max_bidder_id', 'category', 'size']
    search_fields = ['name', 'description', 'category']
    list_filter = ['product_status', 'auction_start_time']
    date_hierarchy = 'auction_start_time'
    ordering = ['auction_start_time']
    fields = ('seller', 'name', 'description', 'image_url', 'min_bid_price', 'bid_increment', 'auction_start_time', 'auction_end_time', 'product_status', 'present_max_bid_price', 'present_max_bidder_id', 'category', 'size')
    # 검색을 위한 추가
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in ['present_max_bid_price', 'present_max_bidder_id']:
            kwargs['required'] = False  # 필수가 아닌 필드로 처리
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['bidder', 'product', 'bid_price', 'bid_time', 'bid_result']
    search_fields = ['bidder__name', 'product__name', 'bid_price']
    list_filter = ['bid_result', 'bid_time']
    date_hierarchy = 'bid_time'
    raw_id_fields = ['bidder', 'product'] # 검색을 위한 추가

@admin.register(Bidder)
class BidderAdmin(admin.ModelAdmin):
    list_display = ['bidder', 'product_id', 'bid_price', 'bid_time']
    search_fields = ['bidder__username', 'product_id__name', 'bid_price']
    list_filter = ['bid_time']
    date_hierarchy = 'bid_time'
    raw_id_fields = ['bidder', 'product_id']