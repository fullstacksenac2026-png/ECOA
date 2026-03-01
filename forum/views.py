from django.shortcuts import render

# Create your views here.
def forum_list(request):
    return render(request, 'forum-list.html')