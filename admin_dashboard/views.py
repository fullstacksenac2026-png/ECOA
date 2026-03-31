from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from authorization.models import User
from pictures.models import Picture, Complaint, Comment
# from forum.models import Thread # Checking if this exists first
from django.db.models import Count

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    # Estatísticas básicas
    total_users = User.objects.count()
    total_pictures = Picture.objects.count()
    total_complaints = Complaint.objects.count()
    total_comments = Comment.objects.count()
    
    # Usuários recentes
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # Denúncias recentes
    recent_complaints = Complaint.objects.all().order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'total_pictures': total_pictures,
        'total_complaints': total_complaints,
        'total_comments': total_comments,
        'recent_users': recent_users,
        'recent_complaints': recent_complaints,
    }
    return render(request, 'admin_dashboard/index.html', context)