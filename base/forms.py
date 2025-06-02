from django.contrib.auth.models import User
from django import forms
from django.db import models



class UserInfoForm(forms.ModelForm):
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input-text input-text--primary-style', 'placeholder': 'Phone number'}),
        required=False,
        label=''
    )
    address1 = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input-text input-text--primary-style', 'placeholder': 'Address 1'}),
        required=False,
        label=''
    )
    address2 = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input-text input-text--primary-style', 'placeholder': 'Address 2'}),
        required=False,
        label=''
    )
    district = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input-text input-text--primary-style', 'placeholder': 'District'}),
        required=False,
        label=''
    )
    city = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input-text input-text--primary-style', 'placeholder': 'City'}),
        required=False,
        label=''
    )

    class Meta:
        fields = ("phone_number", "address1", "address2", "district", "city")
    
    def __init__(self, *args, **kwargs):
        super(UserInfoForm, self).__init__(*args, **kwargs)
        
        self.fields['phone_number'].widget.attrs.update({
            'class': 'input-text input-text--primary-style u-s-m-b-30',
            'placeholder': 'Phone number'
        })
        self.fields['address1'].widget.attrs.update({
            'class': 'input-text input-text--primary-style u-s-m-b-30',
            'placeholder': 'Address 1'
        })
        self.fields['address2'].widget.attrs.update({
            'class': 'input-text input-text--primary-style u-s-m-b-30',
            'placeholder': 'Address 2'
        })
        self.fields['district'].widget.attrs.update({
            'class': 'input-text input-text--primary-style u-s-m-b-30',
            'placeholder': 'District'
        })
        self.fields['city'].widget.attrs.update({
            'class': 'input-text input-text--primary-style u-s-m-b-30',
            'placeholder': 'City'
        })