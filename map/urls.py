from django.urls import path
from . import views

urlpatterns = [
    path('', views.kakao_map_view, name='kakao_map_view'),
]