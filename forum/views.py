from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment, CommentLike, PostLike, View
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
    View.objects.get_or_create(post=post, user=request.user)

    if request.method == 'POST':
        content = request.POST.get('comment_content')
        if content:
            Comment.objects.create(post=post, author=request.user, content=content)

    comments = Comment.objects.filter(post=post, parent__isnull=True).order_by('-created_at')
    paginator = Paginator(comments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    user_like = None
    if request.user.is_authenticated:
        like_obj = post.post_likes.filter(user=request.user).first()
        if like_obj:
            user_like = 'like' if like_obj.is_like else 'dislike'
            
    likes_count = post.post_likes.filter(is_like=True).count()
    dislikes_count = post.post_likes.filter(is_like=False).count()

    return render(request, 'forum-details.html', {
        'post': post,
        'page_obj_comments': page_obj,
        'user_like': user_like,
        'likes_count': likes_count,
        'dislikes_count': dislikes_count,
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

@login_required
def post_update(request, post_id):
    from django.shortcuts import redirect
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        if title and content:
            post.title = title
            post.content = content
            if image:
                post.image = image
            post.save()
            return redirect('forum:forum-post-detail', post_id=post.id)
    return render(request, 'forum-edit.html', {'post': post})

@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('forum:forum-list')
    return render(request, 'forum-confirm-delete.html', {'post': post})

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ['like', 'dislike']:
            is_like = True if action == 'like' else False
            like_obj = PostLike.objects.filter(post=post, user=request.user).first()
            if like_obj:
                if like_obj.is_like == is_like:
                    like_obj.delete()
                else:
                    like_obj.is_like = is_like
                    like_obj.save()
            else:
                PostLike.objects.create(post=post, user=request.user, is_like=is_like)
    return redirect('forum:forum-post-detail', post_id=post.id)

@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ['like', 'dislike']:
            is_like = True if action == 'like' else False
            like_obj = CommentLike.objects.filter(comment=comment, user=request.user).first()
            if like_obj:
                if like_obj.is_like == is_like:
                    like_obj.delete()
                else:
                    like_obj.is_like = is_like
                    like_obj.save()
            else:
                CommentLike.objects.create(comment=comment, user=request.user, is_like=is_like)
    return redirect('forum:forum-post-detail', post_id=comment.post.id)

@login_required
def reply_comment(request, comment_id):
    parent_comment = get_object_or_404(Comment, id=comment_id)
    post = parent_comment.post
    if request.method == 'POST':
        content = request.POST.get('comment_content')
        if content:
            Comment.objects.create(post=post, author=request.user, parent=parent_comment, content=content)
    return redirect('forum:forum-post-detail', post_id=post.id)