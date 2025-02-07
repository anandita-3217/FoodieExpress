from django import forms
from .models import Order, MenuItem

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Restaurant, MenuItem, Order, OrderItem, DeliveryPartner

class RegistrationForm(UserCreationForm):
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'user-type-radio'})
    )
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number'
        })
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Address',
            'rows': 3
        })
    )
    
   
    restaurant_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Restaurant Name'
        })
    )
    restaurant_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Restaurant Description',
            'rows': 3
        })
    )
    cuisine = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cuisine Type'
        })
    )
    is_pure_veg = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    restaurant_photo = forms.URLField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type',
                 'phone_number', 'address']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
        
        
        for field in ['username', 'email', 'password1', 'password2']:
            self.fields[field].help_text = None
            self.fields[field].label = ''

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = self.cleaned_data['user_type']
        
        if commit:
            user.save()
            
            
            if user.user_type == User.RESTAURANT:
                Restaurant.objects.create(
                    owner=user,
                    name=self.cleaned_data['restaurant_name'],
                    description=self.cleaned_data['restaurant_description'],
                    cuisine=self.cleaned_data['cuisine'],
                    is_pure_veg=self.cleaned_data['is_pure_veg'],
                    photo=self.cleaned_data.get('restaurant_photo')
                )
            
            elif user.user_type == User.DELIVERY_PARTNER:
                DeliveryPartner.objects.create(user=user)
                
        return user
    
class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'is_vegetarian', 
                 'is_bestseller', 'availability', 'photo_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'availability': forms.Select(attrs={'class': 'form-control'}),
            'photo_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/image.jpg'
            }),
        }
