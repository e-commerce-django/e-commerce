from django import forms
from .models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'address', 'phone_number']
        widgets = {
            'password': forms.PasswordInput(), 
        }


class UserLoginForm(forms.Form):
    email = forms.EmailField(label='이메일', max_length=200)
    password = forms.CharField(label='비밀번호', widget=forms.PasswordInput)


class UserRegistrationForm(forms.Form):
    email = forms.EmailField(label='이메일', max_length=200)
    username = forms.CharField(label='이름', max_length=40)
    password = forms.CharField(label='비밀번호', widget=forms.PasswordInput)
    address = forms.CharField(label='주소', max_length=200)
    phone_number = forms.CharField(label='전화번호', max_length=20)
