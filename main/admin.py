from django.contrib import admin
from .models import Post

# admin이 게시글에 접근 가능
admin.site.register(Post)