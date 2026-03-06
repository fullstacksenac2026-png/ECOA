from django.shortcuts import render, get_object_or_404
from .models import Post, Comment, CommentLike, CommentDislike, View
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Count


@login_required
def forum_list(request):

    posts = Post.objects.annotate(
        total_views=Count('views', distinct=True),
        total_comments=Count('comments', distinct=True),
        total_likes=Count('likes', distinct=True),
        total_dislikes=Count('dislikes', distinct=True)
    ).order_by('-created_at')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'forum-list.html', {
        'page_obj_post': page_obj,
    })


@login_required
def forum_post_detail(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    comments = Comment.objects.filter(post=post).order_by('-created_at')

    paginator = Paginator(comments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    comment_view = View.objects.filter(post=post)
    comment_like = CommentLike.objects.filter(comment__in=comments)
    comment_dislike = CommentDislike.objects.filter(comment__in=comments)

    return render(request, 'forum-details.html', {
        'post': post,
        'page_obj_comments': page_obj,
        'comment_view': comment_view,
        'comment_like': comment_like,
        'comment_dislike': comment_dislike,
    })

@login_required
def post_create(request):

    if request.method == 'POST':
        return render(request, 'forum-details.html', )
    return render(request, 'forum-create.html', )