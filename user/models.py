from django.contrib.auth.models import AbstractUser, Group, Permission, AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    nickname=models.CharField(max_length=30)

    id = models.CharField(primary_key=True,max_length=20)
    #암호화가 안된 비번을 저장하기 위해 정의
    raw_password = models.CharField(max_length=128, blank=True, null=True)

    #로그인시에 username 필드를 id로 대체하기 위해 추가해준 코드
    USERNAME_FIELD = 'id'

    groups=models.ManyToManyField(Group, related_name="customer_set", blank=True)
    user_permissions= models.ManyToManyField(Permission, related_name="customer_permissions_set", blank=True)

    def __str__(self):
         return self.id

# admin
class UserManager(BaseUserManager):
    def create_user(self, nickname, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not nickname:
            raise ValueError("Nickname is required")
        email = self.normalize_email(email)
        user = self.model(nickname=nickname, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, nickname, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(nickname, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=30, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'nickname'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

# 긴급연락처 저장
class EmergencyContact(models.Model):
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=100, verbose_name="이름")
    phone_number = models.CharField(max_length=15, verbose_name="전화번호")

    class Meta:
            verbose_name = "긴급 연락처"
            verbose_name_plural = "긴급 연락처들"

    def __str__(self):
            return f"{self.user_id.id}의 긴급 연락처: {self.name}"