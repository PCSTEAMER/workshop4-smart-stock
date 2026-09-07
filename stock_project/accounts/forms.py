from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, label="อีเมล", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}))
    first_name = forms.CharField(required=True, label="ชื่อจริง", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=True, label="นามสกุล", widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(required=False, label="เบอร์โทรศัพท์", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0812345678'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            if 'password' in field_name:
                self.fields[field_name].widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("อีเมลนี้ถูกใช้งานในระบบแล้ว กรุณาใช้อีเมลอื่น")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.phone_number = self.cleaned_data['phone_number']
            profile.status = 'pending'  # บังคับให้สถานะเริ่มต้นเป็นรออนุมัติ
            profile.save()
        return user
    
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']
        labels = {
            'username': 'ชื่อผู้ใช้ (Username)',
            'first_name': 'ชื่อจริง',
            'last_name': 'นามสกุล'
        }

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'profile_picture']
        labels = {
            'phone_number': 'เบอร์โทรศัพท์ติดต่อ',
            'profile_picture': 'อัปโหลดรูปโปรไฟล์'
        }