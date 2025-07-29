from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomUser, EmergencyContact
from django.forms import modelformset_factory

# 회원가입
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    nickname=forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = CustomUser
        fields = ['username','nickname','id', 'email','phone_number', 'password1', 'password2']


# 로그인
class LoginForm(forms.Form):
    id=forms.CharField(label='아이디')
    password=forms.CharField(label='비밀번호', widget=forms.PasswordInput)


# 긴급 연락처
class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ['name', 'phone_number']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '이름'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '010-1234-5678'}),
        }
        labels = {
            'name': '긴급 연락처 이름',
            'phone_number': '긴급 연락처 전화번호',
        }

# 긴급 연락처 3개를 한 번에 입력받기 위한 formset
from django.forms import formset_factory

EmergencyContactFormSet = modelformset_factory(
    EmergencyContact,
    form=EmergencyContactForm,
    extra=3, # 기존 연락처가 3개 미만일 때 추가로 보여줄 빈 폼의 개수. max_num을 넘지 않음.
    max_num=3, # 총 긴급 연락처의 최대 개수 (기존 + 신규)
    can_delete=True, # 삭제 체크박스 활성화
    validate_max=True # max_num 유효성 검사 활성화
)