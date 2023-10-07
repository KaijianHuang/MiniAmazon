from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import User
from .models import UserAccount, Address
from django.forms.fields import DateInput, DateField, NumberInput, DateTimeField
from django.core.validators import MaxValueValidator, MinValueValidator

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100,required=True)

    class Meta:
        model = User
        fields = ['username','email','password1','password2','first_name','last_name']

class EditOptionalForm(forms.Form):
    phone = forms.IntegerField()
    cardInfo = forms.IntegerField()
    ups_account_id = forms.IntegerField()

class UserEditForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100,required=True)

class AddAddressForm(forms.Form):
    ADDRESS_TAGS = (('home','home'),('company','company'),('school','school'),('my own tag','my own tag'))
    addressName = forms.CharField(max_length=100,required=True)
    tag = forms.CharField(widget=forms.widgets.Select(choices=ADDRESS_TAGS))
    myTag = forms.CharField(max_length=100, required = False)
    address_x = forms.IntegerField(required=True)
    address_y = forms.IntegerField(required=True)

class PurchaseForm(forms.Form):
    productNum = forms.IntegerField(label='Number of products',required=True,validators=[MinValueValidator(1)])
    address_x = forms.IntegerField(label='Address x',required=True)
    address_y = forms.IntegerField(label='Address y',required=True)
    ups_id = forms.IntegerField(label = 'ups_id', required=False)

class ProductForm(forms.Form):
    productNum = forms.IntegerField(label='Number of products',required=True,validators=[MinValueValidator(1)])
    address_x = forms.IntegerField(label='Address x',required=True)
    address_y = forms.IntegerField(label='Address y',required=True)

class ReportForm(forms.Form):
    email = forms.EmailField(widget=forms.Textarea(attrs={'rows': 1}),required=False, help_text='Enter the email address of the issue reporter.')
    content= forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), required=False)

class AccociateForm(forms.Form):
    ups_id = forms.IntegerField()