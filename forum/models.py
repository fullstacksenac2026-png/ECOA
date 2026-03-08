from django.db import models
from authorization.models import User
# Create your models here.
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')

    image = models.ImageField(upload_to='forum_images/', blank=True, null=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def likes_count(self):
        return self.post_likes.filter(is_like=True).count()
        
    @property
    def dislikes_count(self):
        return self.post_likes.filter(is_like=False).count()
    
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_comments', null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author.username if self.author else "Anonymous"} on {self.post.title}'

    @property
    def likes_count(self):
        return self.likes_set.filter(is_like=True).count()
        
    @property
    def dislikes_count(self):
        return self.likes_set.filter(is_like=False).count()
    
class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')
    is_like = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Like by {self.user.username} on post {self.post.id}'

class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes_set')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes_set')
    is_like = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Like by {self.user.username} on comment {self.comment.id}'
    
class View(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_views')
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'View by {self.user.cpf} on post {self.post.title} at {self.viewed_at}'
    
