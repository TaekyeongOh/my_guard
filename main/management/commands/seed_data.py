import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from main.models import Post, Comment # 'post'를 실제 앱 이름인 'main'으로 수정했습니다.

# User 모델을 가져옵니다.
# CustomUser 모델이 'user' 앱에 있다면 아래와 같이 import 해야 할 수 있습니다.
# from user.models import CustomUser as User
User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with sample data for posts and comments.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('데이터베이스 초기화를 시작합니다...'))

        # 기존 데이터 삭제 (선택 사항)
        Comment.objects.all().delete()
        Post.objects.all().delete()
        # 테스트용으로 생성한 유저만 삭제하기 위해 username으로 필터링
        User.objects.filter(username__startswith='testuser').delete()
        self.stdout.write(self.style.SUCCESS('기존 데이터 삭제 완료.'))

        # 1. 샘플 유저 생성
        users = []
        for i in range(5):
            username = f'testuser{i+1}'
            # 이미 존재하는 유저인지 확인
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password='password123')
                users.append(user)
        self.stdout.write(self.style.SUCCESS(f'{len(users)}명의 샘플 유저 생성 완료.'))

        # 2. 샘플 게시물 데이터 정의
        locations = [
            '서울시 강남구 역삼동', '서울시 마포구 연남동', '서울시 종로구 가회동',
            '서울시 관악구 신림동', '서울시 서초구 반포동', '서울시 성동구 성수동',
            '서울시 영등포구 여의도동', '서울시 강북구 수유동', '서울시 노원구 상계동',
            '서울시 송파구 잠실동', '서울시 용산구 이태원동', '서울시 은평구 불광동'
        ]

        posts_to_create = []
        for location in locations:
            # 각 지역마다 1~3개의 게시물 랜덤 생성
            for _ in range(random.randint(1, 3)):
                author = random.choice(users)
                safety = random.choice(['high', 'medium', 'low'])
                distance = random.choice(['10m', '50m', '100m'])
                
                post_data = {
                    'postname': f'{location} 주변 안전 정보',
                    'contents': f'이곳은 {location}에 위치하고 있으며, 주변 {distance} 내 CCTV가 있습니다. 전반적인 치안 수준은 \'{safety}\' 등급으로 느껴집니다. 밤에도 가로등이 밝고 유동인구가 적당히 있어 안전한 편입니다.',
                    'location': location,
                    'distance': distance,
                    'safety_level': safety,
                    'author': author,
                    'view_count': random.randint(10, 500)
                }
                posts_to_create.append(Post(**post_data))

        # 3. 게시물 대량 생성 (Bulk Create)
        Post.objects.bulk_create(posts_to_create)
        self.stdout.write(self.style.SUCCESS(f'{len(posts_to_create)}개의 샘플 게시물 생성 완료.'))

        # 4. 생성된 게시물에 '좋아요' 추가
        all_posts = Post.objects.all()
        for post in all_posts:
            # 0명 ~ 모든 유저 수만큼 랜덤하게 '좋아요'를 누른 유저 설정
            likes_count = random.randint(0, len(users))
            liked_users = random.sample(users, likes_count)
            post.like_users.set(liked_users)

        self.stdout.write(self.style.SUCCESS('게시물에 랜덤 좋아요 추가 완료.'))

        # 5. 샘플 댓글 및 대댓글 생성
        comments_to_create = []
        for post in all_posts:
            # 각 게시물에 0~5개의 댓글 랜덤 생성
            for _ in range(random.randint(0, 5)):
                comment_author = random.choice(users)
                comment_data = {
                    'post': post,
                    'author': comment_author,
                    'content': '좋은 정보 감사합니다! 참고하겠습니다.',
                }
                comments_to_create.append(Comment(**comment_data))

        Comment.objects.bulk_create(comments_to_create)
        self.stdout.write(self.style.SUCCESS(f'{len(comments_to_create)}개의 샘플 댓글 생성 완료.'))
        
        # 대댓글 생성
        all_comments = Comment.objects.all()
        if all_comments:
            for _ in range(len(all_comments) // 2): # 전체 댓글의 50%에 대해 대댓글 생성
                parent_comment = random.choice(all_comments)
                reply_author = random.choice(users)
                
                # 자기 자신에게 대댓글 달지 않도록 처리
                if parent_comment.author != reply_author and not parent_comment.parent:
                    Comment.objects.create(
                        post=parent_comment.post,
                        author=reply_author,
                        content='저도 동의합니다!',
                        parent=parent_comment
                    )
            self.stdout.write(self.style.SUCCESS('샘플 대댓글 생성 완료.'))


        self.stdout.write(self.style.SUCCESS('데이터베이스 샘플 데이터 구축이 성공적으로 완료되었습니다.'))
