from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'min_bid_price', 'auction_start_time', 'auction_end_time', 'product_status', 'category', 'size']
    search_fields = ['name', 'description', 'category']
    list_filter = ['product_status', 'auction_start_time']
    date_hierarchy = 'auction_start_time'
    ordering = ['auction_start_time']
    fields = ('seller', 'name', 'description', 'image_url', 'min_bid_price', 'bid_increment', 'auction_start_time', 'auction_end_time', 'product_status', 'present_max_bid_price', 'category', 'size')
    # Optionally add 'raw_id_fields' if you have a ForeignKey that can have a lot of entries