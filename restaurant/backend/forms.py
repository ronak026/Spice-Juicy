from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Profile, Address

# Form for updating user information
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'name', 'phone']

# Custom user registration form
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email Address')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username


# Custom authentication form to use email instead of username
class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email and password:
            try:
                user_obj = User.objects.get(email=email)
                username = user_obj.username
                user = authenticate(username=username, password=password)
                if not user:
                    raise forms.ValidationError('Invalid email or password')
                self.user = user
            except User.DoesNotExist:
                raise forms.ValidationError('Invalid email or password')
        return self.cleaned_data

    def get_user(self):
        return getattr(self, 'user', None)

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['line1', 'city', 'state', 'pincode']
        widgets = {
            'line1': forms.TextInput(attrs={'placeholder': 'Street / Building / Area'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'placeholder': 'State'}),
            'pincode': forms.TextInput(attrs={'placeholder': 'Pincode'}),
        }
    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if not pincode.isdigit() or len(pincode) != 6:
            raise ValidationError("Enter a valid 6-digit pincode.")
        return pincode