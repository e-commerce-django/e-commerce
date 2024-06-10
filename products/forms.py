from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    # 가격 선택박스
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
    # 카테고리 선택박스
    CATEGORY_CHOICES = [
        ('스니커즈', '스니커즈'),
        ('운동화', '운동화'),
        ('구두', '구두'),
        ('부츠', '부츠'),
        ('플렛 슈즈', '플렛 슈즈'),
        ('로퍼', '로퍼'),
        ('샌들', '샌들'),
        ('슬리퍼', '슬리퍼'),
        ('기타 신발', '기타 신발'),
    ]
    # 사이즈 선택박스
    SIZE_CHOICES = [(size, str(size)) for size in range(210, 301, 5)]


    bid_increment = forms.ChoiceField(choices=BID_INCREMENT_CHOICES, label='입찰 증가 단위')
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, label='카테고리')
    size = forms.ChoiceField(choices=SIZE_CHOICES, label='사이즈')
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'data-role': 'tagsinput'}), required=False, label='태그')


    class Meta:        
        model = Product
        fields = ['name', 'description', 'image_url', 'min_bid_price', 'bid_increment', 'auction_start_time', 'auction_end_time', 'category', 'size', 'tags']
        exclude = ['seller'] # 판매자 폼에서 입력 X
        labels = {
            'name': '상품명',
            'description': '상품 설명',
            'image_url': '이미지 URL',
            'min_bid_price': '최소 입찰가',
            'auction_start_time': '경매 시작 시간',
            'auction_end_time': '경매 종료 시간',
            'tags': '태그'
        }
        widgets = {
            'auction_start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}), # 캘린더 뷰 위젯 설정
            'auction_end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
            self.seller = kwargs.pop('seller', None)  # seller를 인자로 받음
            super().__init__(*args, **kwargs)

    def save(self, commit=True):
            instance = super().save(commit=False)
            if self.seller:
                instance.seller = self.seller  # 폼 생성 시 seller 설정
            if commit:
                instance.save()
            return instance

    # 최소 입찰가 설정(0보다 작거나 같지 않게)
    def clean_min_bid_price(self):
        min_bid_price = self.cleaned_data.get('min_bid_price')
        if min_bid_price <= 0:
            raise forms.ValidationError('최소 입찰가는 0보다 커야 합니다')
        return min_bid_price

