from django.db import models
from user.models import CustomUser
from django.utils import timezone
# try
from django.contrib.auth import get_user_model

class Post(models.Model):
    postname = models.CharField(max_length=300)
    contents = models.TextField()
    mainphoto = models.ImageField(blank=True, null=True)
    view_count = models.PositiveIntegerField(default=0)

    # 지역 기반 필드 추가
    location = models.CharField(max_length=200, help_text='예: 서울시 강남구 삼성동')
    
    DISTANCE_CHOICES = [
        ('10m', '10m'),
        ('50m', '50m'),
        ('100m', '100m'),
    ]
    distance = models.CharField(max_length=10, choices=DISTANCE_CHOICES, default='10m')

    SAFETY_CHOICES = [
        ('high', '상'),
        ('medium', '중'),
        ('low', '하'),
    ]
    safety_level = models.CharField(max_length=10, choices=SAFETY_CHOICES, default='medium')

    SAFETY_LEVEL_ORDER = {
        'high': 3,
        'medium': 2,
        'low': 1,
    }

    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    like_users = models.ManyToManyField(CustomUser, related_name='liked_posts', blank=True)

    def __str__(self):
        return self.postname

    # 좋아요 수 반환
    def likes_count(self):
        return self.like_users.count()


# 댓글 기능
User = get_user_model()

class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')  # 대댓글
    created_at = models.DateTimeField(auto_now_add=True)
    like_users = models.ManyToManyField(User, related_name='liked_comments', blank=True)  # 댓글 좋아요

    def is_reply(self):
        return self.parent is not None

    def __str__(self):
        return f'{self.author} - {self.content[:20]}'