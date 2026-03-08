from django.db import models
from authorization.models import User
from pictures.models import Picture, Comment
from forum.models import Post as ForumPost, Comment as ForumComment

class Report(models.Model):
    REPORT_CHOICES = [
        ('SPAM', 'Spam ou enganoso'),
        ('INAPPROPRIATE', 'Conteúdo impróprio ou ofensivo'),
        ('FAKE', 'Denúncia falsa'),
        ('OTHER', 'Outro'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_sent')
    picture = models.ForeignKey(Picture, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    forum_post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    forum_comment = models.ForeignKey(ForumComment, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    reason = models.CharField(max_length=50, choices=REPORT_CHOICES)
    description = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = "Imagem" if self.picture else ("Comentário de Imagem" if self.comment else ("Post de Fórum" if self.forum_post else "Comentário de Fórum"))
        return f"Report {self.reason} em {target} por {self.reporter.username}"
