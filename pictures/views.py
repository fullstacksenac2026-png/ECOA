from django.shortcuts import render

# Create your views here.
def historic_pictures(request):
    return render(request, 'historic-pictures.html')