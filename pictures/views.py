from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Picture, Complaint, Geolocation, Verify, TITLE_COMPLAINT_CHOICES
from authorization.models import User
import base64
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
# Lazy load the model to avoid OOM on startup
_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        try:
            from transformers import pipeline
            import torch
            # Load the model only when needed
            _classifier = pipeline("zero-shot-image-classification", model="openai/clip-vit-base-patch32")
        except ImportError:
            return None
    return _classifier

@login_required
def historic_pictures(request):
    pictures = Picture.objects.filter(user=request.user, is_active=True).order_by('-created_at')
    return render(request, 'historic-pictures.html', {'pictures': pictures})

@login_required
def details_pictures(request, picture_id):
    picture = get_object_or_404(Picture, id=picture_id, user=request.user)
    complaints = picture.complaints.all()
    geolocations = picture.geolocations.all()
    verifies = picture.verifies.all()
    return render(request, 'details-picture.html', {
        'picture': picture,
        'complaints': complaints,
        'geolocations': geolocations,
        'verifies': verifies
    })

@login_required
def take_picture(request):
    if request.method == 'POST':
        image_data = request.POST.get('image')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        if not image_data:
            messages.error(request, 'Imagem não fornecida.')
            return redirect('take-picture')

        # Decode base64 image
        try:
            image_data = image_data.split(',')[1]  # Remove data:image/png;base64,
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
        except Exception as e:
            messages.error(request, 'Erro ao processar a imagem.')
            return redirect('take-picture')

        # Prepare image file for Django
       
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        image_file = ContentFile(buffer.getvalue(), name=f'picture_{request.user.id}_{latitude or 0}_{longitude or 0}.png')

        # AI Classification
        candidate_labels = [choice[1] for choice in TITLE_COMPLAINT_CHOICES]
        classifier = get_classifier()
        
        if classifier:
            try:
                results = classifier(image, candidate_labels=candidate_labels)
                top_result = results[0]
                resultado_ia = top_result['label']
                confidence = top_result['score']
            except Exception as e:
                resultado_ia = "Indeterminado"
                confidence = 0.0
        else:
            resultado_ia = "Indeterminado (IA desativada para poupar memória)"
            confidence = 0.0

        # Find the key for the label
        title_key = None
        for key, label in TITLE_COMPLAINT_CHOICES:
            if label == resultado_ia:
                title_key = key
                break

        if not title_key:
            title_key = 'POLUICAO_TERRESTRE'  # Default

        # Save Picture
        picture = Picture.objects.create(
            user=request.user,
            image=image_file,
            title=resultado_ia,
            content=f'Classificado como {resultado_ia} com confiança {confidence:.2f}'
        )

        # Save Geolocation if provided
        if latitude and longitude:
            try:
                Geolocation.objects.create(
                    picture=picture,
                    latitude=float(latitude),
                    longitude=float(longitude)
                )
            except ValueError:
                pass  # Ignore invalid coords

        # Save Complaint
        Complaint.objects.create(
            picture=picture,
            title=title_key,
            content=f'Denúncia automática baseada em IA: {resultado_ia}'
        )

        messages.success(request, 'Imagem processada e salva com sucesso.')
        return render(request, 'take-picture.html', {
            'picture': picture,
            'resultado_ia': f'{resultado_ia} (Confiança: {confidence:.2f})',
            'geolocation': {'latitude': latitude, 'longitude': longitude} if latitude and longitude else None
        })

    return render(request, 'take-picture.html')

@login_required
def create_picture(request):
    
    pass

@login_required
def update_picture(request, picture_id):
    picture = get_object_or_404(Picture, id=picture_id, user=request.user)
    if request.method == 'POST':
        pass
    return render(request, 'update-picture.html', {'picture': picture})

@login_required
def delete_picture(request, picture_id):
    picture = get_object_or_404(Picture, id=picture_id, user=request.user)
    if request.method == 'POST':
        picture.is_active = False
        picture.save()
        messages.success(request, 'Imagem deletada com sucesso.')
        return redirect('historic-pictures')
    return render(request, 'confirm-delete-picture.html', context={'picture': picture})