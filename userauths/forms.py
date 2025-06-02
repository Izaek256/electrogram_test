from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from userauths.models import User

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class':'input-text input-text--primary-style', 'placeholder':'Email Address'}))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'input-text input-text--primary-style', 'placeholder':'First Name'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'input-text input-text--primary-style', 'placeholder':'Last Name'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'input-text input-text--primary-style', 'placeholder': 'User Name'})
        self.fields['password1'].widget.attrs.update({'class': 'input-text input-text--primary-style', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'input-text input-text--primary-style', 'placeholder': 'Confirm Password'})

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'input-text input-text--primary-style'})
        self.fields['password'].widget.attrs.update({'class': 'input-text input-text--primary-style'})

class UpdateUserForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'input-text input-text--primary-style'}))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'input-text input-text--primary-style'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'input-text input-text--primary-style'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'input-text input-text--primary-style'})

class ChangePasswordForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'input-text input-text--primary-style'})
        self.fields['new_password1'].widget.attrs.update({'class': 'input-text input-text--primary-style'})
        self.fields['new_password2'].widget.attrs.update({'class': 'input-text input-text--primary-style'})

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'input-text input-text--primary-style'})
        self.fields['email'].widget.attrs.update({'class': 'input-text input-text--primary-style'})
        self.fields['first_name'].widget.attrs.update({'class': 'input-text input-text--primary-style'})
        self.fields['last_name'].widget.attrs.update({'class': 'input-text input-text--primary-style'})

    def save(self, commit=True):
        user = super(ProfileForm, self).save(commit=False)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user




