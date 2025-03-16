from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class PasswordResetRequestForm(forms.Form):
    """
    密碼重設請求表單
    用戶輸入電子郵件申請重設密碼
    """
    email = forms.EmailField(
        label='電子郵件',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '請輸入註冊時使用的電子郵件'})
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError('此電子郵件未註冊或不存在。')
        return email

class VerificationCodeForm(forms.Form):
    """
    驗證碼表單
    用戶輸入收到的驗證碼
    """
    code = forms.CharField(
        label='驗證碼',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '請輸入6位數驗證碼',
            'autocomplete': 'off'
        })
    )
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code.isdigit():
            raise ValidationError('驗證碼必須是6位數字。')
        return code

class SetPasswordForm(forms.Form):
    """
    設置新密碼表單
    """
    password1 = forms.CharField(
        label='新密碼',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '請輸入新密碼'}),
        validators=[validate_password]
    )
    password2 = forms.CharField(
        label='確認密碼',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '請再次輸入新密碼'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            self.add_error('password2', '兩次輸入的密碼不一致。')
        
        return cleaned_data 