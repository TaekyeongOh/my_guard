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
    # secrets.json에서 API 키를 가져오거나 환경변수에서 가져오기
    secret_file = os.path.join(settings.BASE_DIR, 'secrets.json')
    with open(secret_file) as f:
        secrets = json.loads(f.read())
    GEMINI_API_KEY = secrets.get("GEMINI_API_KEY")
except:
    # 환경변수에서 가져오기
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
        
        # 지역별 안전도 집계
        location_safety = defaultdict(lambda: {'high': 0, 'medium': 0, 'low': 0})
        
        for post in posts:
            if post.location and post.safety_level:
                location_safety[post.location][post.safety_level] += 1
        
        # Gemini API가 없을 경우를 위한 대체 로직
        if not model:
            # 간단한 통계 기반 추천
            recommendations = []
            for location, safety_counts in location_safety.items():
                total = sum(safety_counts.values())
                if total > 0:
                    high_ratio = safety_counts['high'] / total
                    medium_ratio = safety_counts['medium'] / total
                    low_ratio = safety_counts['low'] / total
                    
                    # 안전도 점수 계산 (high: 3점, medium: 2점, low: 1점)
                    safety_score = (high_ratio * 3 + medium_ratio * 2 + low_ratio * 1)
                    recommendations.append({
                        'location': location,
                        'score': safety_score,
                        'counts': safety_counts
                    })
            
            # 점수 순으로 정렬하여 상위 3개 추천
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            top_3 = recommendations[:3]
            
            result_text = "AI 분석 결과 (통계 기반):\n\n"
            for i, rec in enumerate(top_3, 1):
                result_text += f"{i}. {rec['location']}\n"
                result_text += f"   안전도 점수: {rec['score']:.2f}\n"
                result_text += f"   안전도 '상': {rec['counts']['high']}건, '중': {rec['counts']['medium']}건, '하': {rec['counts']['low']}건\n\n"
            
            return JsonResponse({
                'success': True,
                'recommendation': result_text,
                'data': dict(location_safety)
            })
        
        # Gemini API를 통한 추천
        # 프롬프트 생성
        prompt = f"""너는 대한민국 서울의 지역별 안전 전문가야. 내가 제공하는 데이터를 바탕으로, 가장 안전하다고 생각되는 동네 3곳을 추천하고 그 이유를 설명해줘. 답변은 반드시 한국어로 해주고, 각 추천 지역을 목록 형태로 보기 좋게 정리해줘.

[데이터]
"""
        
        for location, safety_counts in location_safety.items():
            prompt += f"\n{location}: 안전도 '상' {safety_counts['high']}건, '중' {safety_counts['medium']}건, '하' {safety_counts['low']}건"
        
        prompt += "\n\n위 데이터를 분석하여 가장 안전한 동네 3곳을 추천해주세요."
        
        # Gemini API 호출
        response = model.generate_content(prompt)
        recommendation_text = response.text
        
        return JsonResponse({
            'success': True,
            'recommendation': recommendation_text,
            'data': dict(location_safety)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
