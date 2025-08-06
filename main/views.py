from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from user.models import CustomUser
from .models import Post, Comment
from .forms import CommentForm
from django.db.models import Q, Count, When, IntegerField, Case

# index.html 페이지를 부르는 index 함수
def index(request):
    return render(request, 'main/index.html')

# blog의 게시글(posting)을 부르는 posting 함수
def posting(request, pk):
    # 게시글(Post) 중 pk(primary_key)를 이용해 하나의 게시글(post)을 검색
    post=get_object_or_404(Post, pk=pk)
    # 조회수 증가
    post.view_count+=1
    post.save()
    
    # author가 None이 아니면 nickname을 가져오고, None이면 '익명'으로 처리
    nickname = post.author.nickname if post.author else '익명'
    
    comments = Comment.objects.filter(post=post)
    comment_form = CommentForm()

    context = {
        'post':post,
        'nickname':nickname,
        'comments':comments,
        'comment_form':comment_form,
    }
    
    # posting.html 페이지를 열 때, 찾아낸 게시글(post)을 post라는 이름으로 가져옴
    return render(request, 'main/posting.html', context)

# new_post 연결 함수
def new_post(request):
    if request.method == 'POST':
        postname = request.POST.get('postname')
        contents = request.POST.get('contents')
        mainphoto = request.FILES.get('mainphoto')
        location = request.POST.get('location')
        distance = request.POST.get('distance')
        safety_level = request.POST.get('safety_level')

        author = request.user

        Post.objects.create(
            postname=postname,
            contents=contents,
            mainphoto=mainphoto,
            author=author,
            location=location,
            distance=distance,
            safety_level=safety_level
        )
        return redirect('/blog/')

    nickname = getattr(request.user, 'nickname')
    return render(request, 'main/new_post.html', {'nickname': nickname})

# 게시글 삭제하는 remove_post 함수 생성
def remove_post(request, pk):
    post = Post.objects.get(pk=pk)
    if request.method == 'POST':
        post.delete()
        return redirect('/blog/')
    return render(request, 'main/remove_post.html', {'Post': post})

# 게시글에 좋아요한 사람 중에 pk가 현재 유저의 pk랑 같은 것이 존재하는지 판단
@require_POST
def like_post(request, post_pk):
    if request.user.is_authenticated:
        post=get_object_or_404(Post, pk=post_pk)

        if post.like_users.filter(pk=request.user.pk).exists():
            post.like_users.remove(request.user)
        else:
            post.like_users.add(request.user)
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('/user/login/')

# 댓글 생성
@require_POST
def comments_create(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    comment_form = CommentForm(request.POST)

    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.post = post
        comment.author = request.user

        parent_id = request.POST.get('parent_id')
        if parent_id:
            parent_comment = get_object_or_404(Comment, pk=parent_id)
            comment.parent = parent_comment

        comment.save()
    return redirect('main:posting', pk=post.pk)


# 댓글 삭제
@require_POST
def comments_delete(request, post_pk, comment_pk):
    if request.user.is_authenticated:
        comment = get_object_or_404(Comment, pk=comment_pk)
        if request.user == comment.author:
            comment.delete()
    return redirect('main:posting', pk=post_pk)

# 댓글에 좋아요
@require_POST
def like_comment(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    user = request.user

    if user in comment.like_users.all():
        comment.like_users.remove(user)
    else:
        comment.like_users.add(user)

    return redirect('main:posting', pk=comment.post.pk)

# blog함수 생성
def blog(request):
    search_query = request.GET.get('search', '')
    sort = request.GET.get('sort', 'recent')

    postlist = Post.objects.all()

    if search_query:
        postlist = postlist.filter(postname__icontains=search_query)

    # 정렬 처리
    if sort == 'recent':
        postlist = postlist.order_by('-created_at')
    elif sort == 'popular':
        postlist = postlist.order_by('-view_count')
    elif sort == 'safety_high':
        postlist = postlist.annotate(
            safety_order=Case(
                When(safety_level='high', then=3),
                When(safety_level='medium', then=2),
                When(safety_level='low', then=1),
                default=0,
                output_field=IntegerField(),
            )
        ).order_by('-safety_order')
    elif sort == 'safety_low':
        postlist = postlist.annotate(
            safety_order=Case(
                When(safety_level='high', then=3),
                When(safety_level='medium', then=2),
                When(safety_level='low', then=1),
                default=0,
                output_field=IntegerField(),
            )
        ).order_by('safety_order')

    return render(request, 'main/blog.html', {
        'postlist': postlist,
        'search_query': search_query,
        'sort': sort
    })