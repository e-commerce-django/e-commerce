from django import forms
from .models import Product

class ProductForm(forms.ModelForm):

    BID_INCREMENT_CHOICES = [
        (500, ' 500₩'),
        (1000, ' 1,000₩'),
        (5000, ' 5,000₩'),
        (10000, ' 10,000₩'),
        (30000, ' 30,000₩'),
        (50000, ' 50,000₩'),
        (100000, ' 100,000₩'),
        (200000, ' 200,000₩'),
        (300000, ' 300,000₩'),
        (500000, ' 500,000₩'),
        (1000000, ' 1,000,000₩')
    ]

    bid_increment = forms.ChoiceField(choices=BID_INCREMENT_CHOICES)

    class Meta:        
        model = Product
        fields = ['name', 'description', 'image_url', 'min_bid_price', 'bid_increment', 'auction_start_time', 'auction_end_time', 'category', 'size']
        widgets = {
            'auction_start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'auction_end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    # Add any custom validations here, for example:
    def clean_min_bid_price(self):
        min_bid_price = self.cleaned_data.get('min_bid_price')
        if min_bid_price <= 0:
            raise forms.ValidationError('The minimum bid price must be greater than zero.')
        return min_bid_price

