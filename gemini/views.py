from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from main.models import Post
from collections import defaultdict
import google.generativeai as genai
import json
import os
from django.conf import settings

# Gemini API 설정
try:
    secret_file = os.path.join(settings.BASE_DIR, 'secrets.json')
    with open(secret_file) as f:
        secrets = json.loads(f.read())
    GEMINI_API_KEY = secrets.get("GEMINI_API_KEY")
except:
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    model = None

@require_http_methods(["GET"])
def get_gemini_recommendation(request):
    """Gemini 추천 페이지를 렌더링합니다."""
    return render(request, 'gemini/gemini_recommend.html')

@csrf_exempt
@require_http_methods(["GET"])
def get_recommendation_data(request):
    """Gemini API를 통해 안전 지역 추천을 받아옵니다."""
    try:
        # 데이터베이스에서 Post 데이터 조회 및 집계
        posts = Post.objects.all()
        location_safety = defaultdict(lambda: {'high': 0, 'medium': 0, 'low': 0, 'reviews': []})
        
        for post in posts:
            if post.location and post.safety_level:
                location_safety[post.location][post.safety_level] += 1
                if post.contents and len(post.contents.strip()) > 0:
                    location_safety[post.location]['reviews'].append(post.contents.strip())
        
        # 각 지역 안전도 점수 계산
        recommendations = []
        for location, data in location_safety.items():
            total = sum([data['high'], data['medium'], data['low']])
            if total > 0:
                high_ratio = data['high'] / total
                medium_ratio = data['medium'] / total
                low_ratio = data['low'] / total
                safety_score = (high_ratio * 3 + medium_ratio * 2 + low_ratio * 1)
                recommendations.append({
                    'location': location,
                    'score': safety_score,
                    'counts': {'high': data['high'], 'medium': data['medium'], 'low': data['low']},
                    'reviews': data['reviews']
                })
        
        # 점수 순으로 상위 3개 지역 추출
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        top_3 = recommendations[:3]
        
        result_text = "AI 분석 결과:\n\n"
        safety_keywords = ['안전', 'CCTV', '가로등', '지구대', '밝음', '사람', '공원', '골목', '순찰']

        for i, rec in enumerate(top_3, 1):
            result_text += f"{i}. {rec['location']}\n"
            result_text += f"   안전도 점수: {rec['score']:.2f}\n"
            result_text += f"   안전도 '상': {rec['counts']['high']}건, '중': {rec['counts']['medium']}건, '하': {rec['counts']['low']}건\n"
            
            if rec['reviews']:
                reviews_text = rec['reviews'][:3]  # 최대 3개 후기 사용
                if model:
                    # Gemini API가 있으면 AI에게 후기 요약 요청
                    prompt = f"아래 후기 내용을 분석해서, 안전과 관련된 이유만 1-2줄로 요약해 추천 이유를 작성하세요. 후기 원문은 표시하지 마세요.\n{reviews_text}"
                    summary = model.generate_content(prompt).text
                else:
                    # 모델이 없으면 후기 키워드 기반 요약
                    found_keywords = set()
                    for review in reviews_text:
                        for kw in safety_keywords:
                            if kw in review:
                                found_keywords.add(kw)
                    if found_keywords:
                        summary = f"{', '.join(found_keywords)} 등 시설과 환경이 잘 갖추어져 있어 안전합니다."
                    else:
                        summary = "안전도가 높아 추천할 만한 지역입니다."
                
                result_text += f"   추천 이유: {summary}\n"
            else:
                result_text += f"   추천 이유: 안전도 점수가 높아 추천합니다.\n"
            result_text += "\n"

        return JsonResponse({
            'success': True,
            'recommendation': result_text,
            'data': dict(location_safety)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
