import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from main.models import Post, Comment

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with diverse sample data for posts and comments.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('데이터베이스 초기화를 시작합니다...'))

        # 0. 기존 데이터 삭제
        Comment.objects.all().delete()
        Post.objects.all().delete()
        User.objects.filter(username__startswith='testuser').delete()
        self.stdout.write(self.style.SUCCESS('기존 데이터 삭제 완료.'))

        # 1. 샘플 유저 생성
        users = []
        for i in range(5):
            username = f'testuser{i+1}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password='password123')
                users.append(user)
        self.stdout.write(self.style.SUCCESS(f'{len(users)}명의 샘플 유저 생성 완료.'))

        # 2. 위치, 템플릿 정의
        locations = [
            '서울 강남구 역삼동', '서울 마포구 연남동', '서울 종로구 가회동',
            '서울 관악구 신림동', '서울 서초구 반포동', '서울 성동구 성수동',
            '서울 영등포구 여의도동', '서울 강북구 수유동', '서울 노원구 상계동',
            '서울 송파구 잠실동', '서울 용산구 이태원동', '서울 은평구 불광동'
        ]

        # 게시물 내용 템플릿
        content_fragments = {
            'safety': [
                '치안이 매우 안정적인 지역입니다.',
                '조심할 필요가 있는 지역이지만 주간에는 안전합니다.',
                '밤길은 조금 위험할 수 있으니 주의하세요.',
                'CCTV가 잘 설치되어 있어 안심할 수 있습니다.'
            ],
            'lighting': [
                '가로등이 밝아 밤에도 길을 걷기 편합니다.',
                '어두운 골목이 일부 있어 주의가 필요합니다.',
                '밤에도 주변이 잘 보이는 편입니다.'
            ],
            'crowd': [
                '주민과 상가 이용객이 많아 활기찬 지역입니다.',
                '유동인구가 적은 조용한 지역입니다.',
                '적당한 사람들이 있어 혼자 다녀도 큰 위험은 없습니다.'
            ],
            'facilities': [
                '인근 경찰서와 편의시설이 가까워 안심됩니다.',
                '주변 상가와 카페가 많아 사람들의 왕래가 활발합니다.',
                '공원과 광장이 있어 주변 환경이 쾌적합니다.'
            ],
            'transport': [
                '대중교통 접근성이 좋아 이동이 편리합니다.',
                '주차 공간이 충분하고 교통량도 적당합니다.'
            ]
        }

        safety_level_map = {
            'high': 'high',
            'medium': 'medium',
            'low': 'low'
        }

        # 3. 게시물 생성
        posts_to_create = []
        for _ in range(30):
            location = random.choice(locations)
            author = random.choice(users)
            distance = random.choice(['10m', '50m', '100m'])
            safety = random.choice(['high', 'medium', 'low'])

            # 각 게시물마다 내용 조합 랜덤 (1~5개 조각)
            num_fragments = random.randint(1, 5)
            chosen_keys = random.sample(list(content_fragments.keys()), num_fragments)
            contents_list = [random.choice(content_fragments[key]) for key in chosen_keys]
            contents_text = " ".join(contents_list) + f" 주변 {distance} 내 CCTV가 확인되었습니다."

            post_data = {
                'postname': f'{location} 주변 안전 정보',
                'contents': contents_text,
                'location': location,
                'distance': distance,
                'safety_level': safety_level_map[safety],
                'author': author,
                'view_count': random.randint(10, 500)
            }
            posts_to_create.append(Post(**post_data))

        Post.objects.bulk_create(posts_to_create)
        self.stdout.write(self.style.SUCCESS(f'{len(posts_to_create)}개의 샘플 게시물 생성 완료.'))

        # 4. 게시물에 랜덤 좋아요 추가
        all_posts = Post.objects.all()
        for post in all_posts:
            likes_count = random.randint(0, len(users))
            liked_users = random.sample(users, likes_count)
            post.like_users.set(liked_users)
        self.stdout.write(self.style.SUCCESS('게시물에 랜덤 좋아요 추가 완료.'))

        # 5. 샘플 댓글 생성
        comment_texts = [
            '좋은 정보 감사합니다!', '참고가 되네요.', '저도 여기를 자주 다니는데 안전합니다.',
            '밤길 걱정했는데 안심되네요.', 'CCTV 정보까지 상세하네요!', '주변 상가가 많아 편리합니다.',
            '가로등이 밝아 좋습니다.', '동감합니다.', '조금 위험할 수 있겠네요.', '좋은 팁 공유 감사합니다.'
        ]

        comments_to_create = []
        for post in all_posts:
            for _ in range(random.randint(1, 3)):
                comment_author = random.choice(users)
                comment_data = {
                    'post': post,
                    'author': comment_author,
                    'content': random.choice(comment_texts),
                }
                comments_to_create.append(Comment(**comment_data))
        Comment.objects.bulk_create(comments_to_create)
        self.stdout.write(self.style.SUCCESS(f'{len(comments_to_create)}개의 샘플 댓글 생성 완료.'))

        # 6. 대댓글 생성
        reply_texts = [
            '저도 동의합니다!', '좋은 의견이에요.', '참고하겠습니다!', '정말 맞는 말씀입니다.', '동감합니다.'
        ]
        all_comments = Comment.objects.all()
        for _ in range(len(all_comments)//2):
            parent_comment = random.choice(all_comments)
            reply_author = random.choice(users)
            if parent_comment.author != reply_author and not parent_comment.parent:
                Comment.objects.create(
                    post=parent_comment.post,
                    author=reply_author,
                    content=random.choice(reply_texts),
                    parent=parent_comment
                )
        self.stdout.write(self.style.SUCCESS('샘플 대댓글 생성 완료.'))

        self.stdout.write(self.style.SUCCESS('데이터베이스 샘플 데이터 구축이 성공적으로 완료되었습니다.'))
