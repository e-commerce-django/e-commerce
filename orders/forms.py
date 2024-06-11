from django import forms

class PaymentForm(forms.Form):
    card_number = forms.CharField(label='카드 번호', max_length=16)
    expiry = forms.CharField(label='만료일 (MM/YY)', max_length=5)
    birth = forms.CharField(label='생년월일 6자리', max_length=6)
    pwd_2digit = forms.CharField(label='카드 비밀번호 앞 2자리', max_length=2)
