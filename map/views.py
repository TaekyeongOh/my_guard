from django.shortcuts import render
from django.conf import settings

def index(request):
    return render(request, 'map/map.html')

# 네이버 지도 api
# def map_view(request):
#     naver_maps_client_id = settings.NAVER_MAPS_CLIENT_ID
#     return render(request, 'map/map.html', {
#         'naver_maps_client_id': naver_maps_client_id
#     })

def kakao_map_view(request):
    kakao_maps_app_key = settings.KAKAO_MAPS_APP_KEY
    return render(request, 'map/map.html', {
        'kakao_maps_app_key': kakao_maps_app_key
    })
