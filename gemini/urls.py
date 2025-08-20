from django.urls import path
from . import views

app_name = 'gemini'

urlpatterns = [
    path('', views.get_gemini_recommendation, name='gemini_recommendation'),
    path('api/', views.get_recommendation_data, name='get_recommendation_data'),
]
