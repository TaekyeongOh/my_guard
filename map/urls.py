from django.urls import path
from . import views

urlpatterns = [
    path('', views.kakao_map_view, name='kakao_map_view'),
    path('search/', views.kakao_map_search_view, name='kakao_map_search_view'),

]