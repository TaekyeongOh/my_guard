from django.urls import path
from . import views
from main.views import *
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views

app_name='main'

urlpatterns=[
    path('', views.index, name='index'),
    path('blog/',views.blog,  name='blog'),
    path('blog/<int:pk>/', views.posting, name="posting"),
    path('blog/new_post/', views.new_post, name="new_post"),
    path('blog/<int:pk>/remove/', views.remove_post, name="remove_post"),
    path('blog/<int:post_pk>/like_post/', views.like_post, name='like_post'),

    # 댓글 작성, 삭제에 사용되는 url
    path('blog/<int:post_pk>/comments/', views.comments_create, name='comments_create'),
    path('blog/<int:post_pk>/comments/<int:comment_pk>/delete/', views.comments_delete, name='comments_delete'),
    path('comments/<int:comment_pk>/like/', views.like_comment, name='like_comment'),

]

# 이미지 URL 설정
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)