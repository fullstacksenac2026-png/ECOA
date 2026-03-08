from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Report
from pictures.models import Picture, Comment
from forum.models import Post as ForumPost, Comment as ForumComment
from .forms import ReportForm

@login_required
def report_picture(request, picture_id):
    picture = get_object_or_404(Picture, id=picture_id)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.picture = picture
            report.save()
            messages.success(request, 'Sua denúncia foi registrada.')
            return redirect('pictures:details-picture', picture_id=picture.id)
    else:
        form = ReportForm()
    return render(request, 'report_form.html', {'target': picture, 'type': 'picture', 'form': form})

@login_required
def report_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.comment = comment
            report.save()
            messages.success(request, 'Comentário denunciado com sucesso.')
            return redirect('pictures:details-picture', picture_id=comment.picture.id)
    else:
        form = ReportForm()
    return render(request, 'report_form.html', {'target': comment, 'type': 'comment', 'form': form})

@login_required
def report_forum_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.forum_post = post
            report.save()
            messages.success(request, 'Post do Fórum denunciado com sucesso.')
            return redirect('forum:forum-post-detail', post_id=post.id)
    else:
        form = ReportForm()
    return render(request, 'report_form.html', {'target': post, 'type': 'forum_post', 'form': form})

@login_required
def report_forum_comment(request, comment_id):
    comment = get_object_or_404(ForumComment, id=comment_id)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.forum_comment = comment
            report.save()
            messages.success(request, 'Comentário do fórum denunciado com sucesso.')
            return redirect('forum:forum-post-detail', post_id=comment.post.id)
    else:
        form = ReportForm()
    return render(request, 'report_form.html', {'target': comment, 'type': 'forum_comment', 'form': form})
