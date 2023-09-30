from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *


class CheckoutForm(forms.ModelForm):
    class Meta:
        model= BillingAddress
        fields = ['address','receiver', 'phone_no', 'country','city', 'zip', 'save_info', 'instructions']
        widgets = {
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 1 ,'style': 'padding: 10px;'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name != 'instructions':
                field = self.fields[field_name]
                field.widget.attrs.update({'class': 'form-control'})


class CustomUserForm(UserCreationForm):
    class Meta:
        model= User
        fields=['username','email','password1','password2']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs.update({'class': 'form-control'})
    