from django.shortcuts import render, get_object_or_404
from .models import Post, Comment, CommentLike, CommentDislike, View
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Count


@login_required
def forum_list(request):
    search_query = request.GET.get('search_post', '')
    if search_query:
        posts = Post.objects.filter(title__icontains=search_query)
    else:
        posts = Post.objects.all()

    posts = posts.annotate(
        total_views=Count('views', distinct=True),
        total_comments=Count('comments', distinct=True)
    ).order_by('-created_at')

    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'forum-list.html', {
        'page_obj_post': page_obj,
    })


@login_required
def forum_post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # View tracking
    View.objects.get_or_create(post=post, user=request.user.username)

    if request.method == 'POST':
        content = request.POST.get('comment_content')
        if content:
            Comment.objects.create(post=post, content=content)

    comments = Comment.objects.filter(post=post).order_by('-created_at')
    paginator = Paginator(comments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'forum-details.html', {
        'post': post,
        'page_obj_comments': page_obj,
    })

@login_required
def post_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        if title and content:
            post = Post.objects.create(user=request.user, title=title, content=content, image=image)
            from django.shortcuts import redirect
            return redirect('forum:forum-post-detail', post_id=post.id)
    return render(request, 'forum-create.html')