from django.shortcuts import render
from django.template.loader import get_template
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from user.forms import SignUpForm
## github

from django.template import engines
from django.contrib.auth import logout


#홈화면 렌더링
def home_view(request):
    return render(request,'home.html')

#로그아웃 기능 구현
def logout_view(request):
    logout(request)
    return render(request,'home.html')

# 내 코드
@login_required
def home(request):
    print(f"현재 로그인한 사용자: {request.user.nickname}")
    return render(request, "home.html", {'nickname':request.user.nickname})

def signupView(request):
    if request.method =='POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('signup')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form':form})

