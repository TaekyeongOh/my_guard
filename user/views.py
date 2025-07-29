from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login
from django.contrib import messages
from django.http import JsonResponse
from .forms import SignUpForm, LoginForm, EmergencyContactFormSet
from .models import CustomUser, EmergencyContact
from django.contrib.auth.decorators import login_required


#회원가입 기능
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        user_id = request.POST.get('id')
        if form.is_valid():
            form.save()
            #비밀번호 찾기시에 암호화된 비밀번호가 아닌 실제 비번을 불러와야하기 때문에 따로 필드에 저장시켜줌
            user= CustomUser.objects.get(id=user_id)
            user.raw_password=request.POST.get('password1')
            user.save()
            return redirect('user/signup') 
    else:
        form = SignUpForm()
    return render(request, 'user/signup.html', {'form': form})

#로그인 기능
def login_view(request):
    form = LoginForm()  

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            id = form.cleaned_data['id']
            password = form.cleaned_data['password']

            #기존 authenticate의 경우 username과 pwd를 바탕으로 유효한 유저인지 검증을 하나, 이 함수를 커스터마이즈하여
            #id와 pwd를 기준으로 유효한 유저인지 검증을 하고 싶어서 다음과 같이 바꿔줌.
            #이 코드에서 사용자가 제출한 id와 pwd가 실제 db에 있는 유저인지 검증
            user = authenticate(request, username=id, password=password)

            print (f'views.py, user: {user}, id: {id}, password: {password}')

            if user is not None:
                #user 변수에 재대로 유저변수가 들어옴 = 로그인 진행시켜!(회원가입을 했던 유저이므로)
                login(request, user)
                # 로그인 성공 후 사용자 정보를 템플릿으로 전달
                return JsonResponse({
                    'id': user.id,
                    'username': user.username,
                    'nickname':user.nickname,
                    'is_authenticated': True,
                    'redirect_url': '/',
                    })
                #로그인 후에는 홈화면으로 리다이렉트
                # return redirect('home')
            else:
                #db에 해당하는 유저가 없으면 해당하는 유저가 없다고 팝업을 띄운다.
                messages.error(request, '해당하는 유저가 없습니다!')

    return render(request, 'user/login.html', {'form': form})


#비밀번호 찾기 기능(아이디를 입력하면 그에 해당하는 유저의 비밀번호를 반환해주는 형식)
def password_search(request):
    if request.method == 'POST':
        user_id = request.POST.get('id')  # 폼에서 입력한 id 값을 user_id 변수에 저장
        found_password=""

        try:
            # CustomUser 테이블에 해당 ID가 있는지 확인
            exist_user = CustomUser.objects.get(id=user_id)
            #해당 유저의 비밀번호를 불러옴
            found_password=exist_user.raw_password
        except CustomUser.DoesNotExist:
            messages.error(request, '해당 아이디를 가진 유저가 없습니다.')
    
        return render(request, 'user/password.html', {'found_password' :found_password})
        
    return render(request,'user/password.html')

# 긴급연락처
@login_required
def manage_emergency_contacts_view(request):
    queryset = EmergencyContact.objects.filter(user_id=request.user)

    if request.method == 'POST':
        formset = EmergencyContactFormSet(request.POST, request.FILES, queryset=queryset)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                # 새로운 인스턴스에만 user_id를 할당합니다.
                # 기존 인스턴스는 이미 user_id를 가지고 있습니다.
                if not instance.pk: # pk가 없으면 새로운 인스턴스입니다.
                    instance.user_id = request.user
                instance.save() # 인스턴스 저장

            # 삭제된 폼 처리 (can_delete=True일 때 필요)
            for obj in formset.deleted_objects:
                obj.delete()

            messages.success(request, "긴급 연락처가 성공적으로 저장되었습니다.")
            return redirect('/') # 저장 후 메인 페이지로 리다이렉트 (URL 이름 확인)
        else:
            messages.error(request, '긴급 연락처 저장에 실패했습니다. 입력 양식을 확인해주세요.')
    else:
        formset = EmergencyContactFormSet(queryset=queryset)

    return render(request, 'user/emergency_contacts.html', {'formset': formset})