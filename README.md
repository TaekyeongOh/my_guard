# 마이가드 (My Guard) - AI 안전 지역 추천 시스템

## 프로젝트 개요
마이가드는 Django 기반의 안전 정보 공유 플랫폼으로, 사용자들이 지역별 안전 정보를 공유하고 AI를 통해 가장 안전한 거주 지역을 추천받을 수 있습니다.

## 주요 기능
- 사용자 인증 및 관리
- 지역별 안전 정보 게시 및 공유
- 지도 기반 안전 정보 시각화
- **AI 기반 안전 지역 추천 (Gemini)**

## AI 안전 지역 추천 기능 설정

### 1. Gemini API 키 설정
1. [Google AI Studio](https://makersuite.google.com/app/apikey)에서 API 키를 발급받습니다.
2. 프로젝트 루트에 `secrets.json` 파일을 생성하고 다음 내용을 추가합니다:

```json
{
    "SECRET_KEY": "your-django-secret-key",
    "KAKAO_MAPS_APP_KEY": "your-kakao-maps-api-key",
    "GEMINI_API_KEY": "your-gemini-api-key"
}
```

### 2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 데이터베이스 마이그레이션
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 개발 서버 실행
```bash
python manage.py runserver
```

## 사용법

### AI 안전 지역 추천
1. 브라우저에서 `http://127.0.0.1:8000/gemini/` 접속
2. "AI에게 추천받기" 버튼 클릭
3. AI가 분석한 안전 지역 추천 결과 확인

### 기타 기능
- 메인 페이지: `http://127.0.0.1:8000/`
- 지도 검색: `http://127.0.0.1:8000/map/`
- 사용자 관리: `http://127.0.0.1:8000/user/`

## 기술 스택
- **Backend**: Django 4.2+
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **AI**: Google Gemini Pro
- **Database**: SQLite (개발용)
- **Maps**: Kakao Maps API

## 프로젝트 구조
```
my_guard/
├── main/           # 메인 앱 (게시글, 댓글)
├── user/           # 사용자 관리 앱
├── map/            # 지도 기능 앱
├── gemini/         # AI 추천 기능 앱 (신규)
├── templates/      # HTML 템플릿
├── static/         # 정적 파일 (CSS, JS, 이미지)
└── myproject/      # 프로젝트 설정
```

## 주의사항
- Gemini API 키가 설정되지 않은 경우, 통계 기반의 기본 추천 기능이 동작합니다.
- 실제 서비스 배포 시에는 환경변수를 통한 API 키 관리가 권장됩니다.
- 데이터베이스에 충분한 Post 데이터가 있어야 의미있는 추천이 가능합니다.
