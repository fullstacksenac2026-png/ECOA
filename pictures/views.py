from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.db.models import Q, Count
from .models import Picture, Complaint, Geolocation, Verify, TITLE_COMPLAINT_CHOICES, Comment, Like
from .forms import ComplaintForm, PictureUpdateForm
from .ai_model import AIModelManager, verify_image, classify_image_pollution, get_chatbot_response
from authorization.models import User
import base64
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
import os
import logging
from django.core.paginator import Paginator
from django.http import JsonResponse
import json

logger = logging.getLogger(__name__)

# ML packages - optional, app works without them
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import tensorflow as tf
    import tensorflow_hub as hub
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False



def is_low_capacity(request):
    """Detecta se o dispositivo é móvel ou tem restrição de processamento."""
    ua = request.META.get('HTTP_USER_AGENT', '').lower()
    is_mobile = any(word in ua for word in ['mobile', 'android', 'iphone', 'phone', 'ipod', 'tablet', 'ipad'])
    
    # Verifica headers de economia de dados
    is_low_data = request.META.get('HTTP_SAVE_DATA') == 'on'
    
    # Verifica header de conexão (rede lenta)
    connection = request.META.get('HTTP_CONNECTION', '').lower()
    is_slow_connection = 'slow' in connection or 'limited' in connection
    
    return is_mobile or is_low_data or is_slow_connection


@login_required
def verify_image_ai(request):
    """
    API endpoint para verificar se uma imagem é real ou fake
    Usa modelo de deepfake detection
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        # Obter imagem
        image_data = request.POST.get('image')
        if not image_data:
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                image = Image.open(image_file)
            else:
                return JsonResponse({'error': 'Nenhuma imagem fornecida'}, status=400)
        else:
            # Decode base64
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
        
        # Verificar com IA
        result = verify_image(image)
        
        return JsonResponse({
            'success': True,
            'is_fake': result['is_fake'],
            'confidence': result['confidence'],
            'score': result['score'],
            'message': result['message'],
            'recommendation': result['recommendation']
        })
    except Exception as e:
        logger.error(f"Erro na verificação de imagem: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def classify_image_api(request):
    """
    API endpoint para classificar uma imagem
    Retorna categorias de poluição
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        # Obter imagem
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            image = Image.open(image_file)
        elif request.POST.get('image'):
            image_data = request.POST.get('image')
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
        else:
            return JsonResponse({'error': 'Nenhuma imagem fornecida'}, status=400)
        
        # Classificar com IA
        result = classify_image_pollution(image)
        
        return JsonResponse({
            'success': True,
            'classifications': result
        })
    except Exception as e:
        logger.error(f"Erro na classificação: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def historic_pictures(request):
    search_query = request.GET.get('search_picture', '')
    filter_type = request.GET.get('filter_type', 'all')
    
    # Base queryset - showing all active pictures
    pictures = Picture.objects.filter(is_active=True)
    
    if search_query:
        pictures = pictures.filter(
            models.Q(title__icontains=search_query) | 
            models.Q(content__icontains=search_query)
        )
        
    if filter_type == 'public':
        pictures = pictures.filter(title__icontains='ambiente público')
    elif filter_type == 'private':
        pictures = pictures.filter(title__icontains='ambiente privado')
    
    # Annotate with counts (similar to forum)
    from django.db.models import Count, Q
    pictures = pictures.annotate(
        total_comments=Count('comments', distinct=True),
        total_likes=Count('likes', filter=Q(likes__is_like=True), distinct=True),
        total_dislikes=Count('likes', filter=Q(likes__is_like=False), distinct=True)
    ).order_by('-created_at')

    paginator = Paginator(pictures, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'historic-pictures.html', {
        'page_obj': page_obj,
        'pictures': page_obj.object_list,
        'search_query': search_query,
        'filter_type': filter_type
    })

from django.core.paginator import Paginator

@login_required
def details_pictures(request, picture_id):
    picture = get_object_or_404(Picture, id=picture_id, is_active=True)
    complaints = Complaint.objects.filter(picture=picture)
    geolocations = Geolocation.objects.filter(picture=picture)
    
    comments_list = picture.comments.filter(parent__isnull=True).annotate(
        likes_count=Count('likes', filter=Q(likes__is_like=True), distinct=True),
        dislikes_count=Count('likes', filter=Q(likes__is_like=False), distinct=True)
    ).order_by('-created_at')
    
    paginator = Paginator(comments_list, 10)
    page_number = request.GET.get('page')
    comments = paginator.get_page(page_number)
    
    user_like = None
    if request.user.is_authenticated:
        like_obj = picture.likes.filter(user=request.user).first()
        if like_obj:
            user_like = 'like' if like_obj.is_like else 'dislike'
            
    likes_count = picture.likes.filter(is_like=True).count()
    dislikes_count = picture.likes.filter(is_like=False).count()
        
    context = {
        'picture': picture,
        'complaints': complaints,
        'geolocations': geolocations,
        'comments': comments,
        'user_like': user_like,
        'likes_count': likes_count,
        'dislikes_count': dislikes_count,
    }

    return render(request, 'details-picture.html', context=context)

@login_required
def create_complaint(request, picture_id):
    picture = get_object_or_404(Picture, id=picture_id, user=request.user, is_active=True)
    verify = picture.verifies.first()
    
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.picture = picture
            complaint.save()

            # Atualiza o resumo visual da Picture
            title_key = complaint.title
            picture.title = dict(TITLE_COMPLAINT_CHOICES).get(title_key, title_key)
            picture.content = complaint.content[:250]
            picture.save()
            
            messages.success(request, '✅ Queixa postada com sucesso! Sua denúncia está visível para todos.')
            
            # Redireciona para o filtro correto
            if 'público' in picture.title.lower():
                return redirect('/pictures/historic/?filter_type=public')
            elif 'privado' in picture.title.lower():
                return redirect('/pictures/historic/?filter_type=private')
                
            return redirect('pictures:historic-pictures')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = ComplaintForm()
            
    return render(request, 'create-complaint.html', {
        'picture': picture,
        'verify': verify,
        'form': form
    })

@login_required
def take_picture(request):
    if request.method == 'POST':
        image_data = request.POST.get('image')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        if not image_data:
            messages.error(request, 'Imagem não fornecida.')
            return redirect('pictures:take-picture')

        if not latitude or not longitude:
            messages.error(request, 'A localização é obrigatória para registrar uma ocorrência.')
            return redirect('pictures:take-picture')

        try:
            image_data_decoded = image_data.split(',')[1] if ',' in image_data else image_data
            image_bytes = base64.b64decode(image_data_decoded)
            image = Image.open(BytesIO(image_bytes))
        except Exception as e:
            logger.error(f"Erro ao processar imagem: {e}")
            messages.error(request, 'Erro ao processar a imagem.')
            return redirect('pictures:take-picture')

        buffer = BytesIO()
        # Converte para RGB se tiver transparência (JPEG não suporta RGBA)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        
        # Criar nome único para arquivo
        import time
        timestamp = int(time.time() * 1000)
        image_file = ContentFile(buffer.getvalue(), name=f'picture_{request.user.id}_{timestamp}.jpg')

        # Usar IA para análise (com fallback)
        is_fake = False
        ai_message = "Imagem recebida"
        detected_place = "Localização detectada"
        
        try:
            logger.info("Iniciando análise de IA da imagem...")
            
            # Verificar se é imagem fake (deepfake detection)
            verify_result = verify_image(image)
            logger.info(f"Resultado da verificação: {verify_result}")
            
            is_fake = verify_result.get('is_fake', False)
            ai_message = verify_result.get('message', "Análise concluída")
            
            # Classificar imagem (poluição, etc.)
            classifications = classify_image_pollution(image)
            logger.info(f"Classificações: {classifications}")
            
            if classifications and len(classifications) > 0:
                detected_place = classifications[0].get('label', detected_place)
        except Exception as e:
            logger.error(f"Erro na análise de IA: {e}", exc_info=True)
            ai_message = f"Análise simplificada realizada"

        try:
            # Criar imagem na base de dados
            picture = Picture.objects.create(
                user=request.user,
                image=image_file,
                title="Aguardando queixa...",
                content=f"Local: {detected_place}"
            )
            logger.info(f"Picture criada: {picture.id}")

            # Criar geolocalização
            if latitude and longitude:
                Geolocation.objects.create(
                    picture=picture,
                    latitude=float(latitude),
                    longitude=float(longitude)
                )
                logger.info(f"Geolocalização criada para: {picture.id}")

            # Criar registro de verificação
            Verify.objects.create(
                picture=picture,
                is_fake=is_fake,
                verify_message=ai_message
            )
            logger.info(f"Verificação criada para: {picture.id}")

            messages.info(request, f'✅ Foto recebida e analisada! Complete as informações para postar no feed.')
            return redirect('pictures:create-complaint', picture_id=picture.id)
            
        except Exception as e:
            logger.error(f"Erro ao criar imagem no banco: {e}", exc_info=True)
            messages.error(request, f'Erro ao salvar imagem: {str(e)}')
            return redirect('pictures:take-picture')

    return render(request, 'take-picture.html')

@login_required
def create_picture(request):
    if request.method == 'POST':
        image_file = request.FILES.get('image')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        if not image_file:
            messages.error(request, 'Imagem não fornecida.')
            return redirect('pictures:create-picture')

        if not latitude or not longitude:
            messages.error(request, 'A localização é obrigatória para registrar uma ocorrência.')
            return redirect('pictures:create-picture')

        # Análise de IA
        is_fake = False
        detected_place = "Localização detectada"
        ai_message = "Imagem recebida"
        
        try:
            from PIL import Image
            img = Image.open(image_file)
            
            logger.info(f"Analisando imagem enviada: {image_file.name}")
            
            # Verificação de deepfake
            verify_result = verify_image(img)
            is_fake = verify_result.get('is_fake', False)
            ai_message = verify_result.get('message', ai_message)
            logger.info(f"Verificação concluída: {ai_message}")
            
            # Classificação
            classifications = classify_image_pollution(img)
            if classifications and len(classifications) > 0:
                detected_place = classifications[0].get('label', detected_place)
                logger.info(f"Classificação: {detected_place}")
        except Exception as e:
            logger.error(f"Erro na análise de IA do upload: {e}", exc_info=True)
            ai_message = "Análise simplificada realizada"

        try:
            # Recarregar imagem para salvar
            image_file.seek(0)
            
            picture = Picture.objects.create(
                user=request.user,
                image=image_file,
                title="Aguardando queixa...",
                content=f"Local: {detected_place}"
            )
            logger.info(f"Picture criada (upload): {picture.id}")

            Geolocation.objects.create(
                picture=picture,
                latitude=float(latitude),
                longitude=float(longitude)
            )
            logger.info(f"Geolocalização criada (upload): {picture.id}")

            Verify.objects.create(
                picture=picture,
                is_fake=is_fake,
                verify_message=ai_message
            )
            logger.info(f"Verificação criada (upload): {picture.id}")

            messages.info(request, '✅ Imagem enviada e analisada! Complete as informações para postar no feed.')
            return redirect('pictures:create-complaint', picture_id=picture.id)
        except Exception as e:
            logger.error(f"Erro ao criar imagem no banco (upload): {e}", exc_info=True)
            messages.error(request, f'Erro ao salvar imagem: {str(e)}')
            return redirect('pictures:create-picture')

    return render(request, 'create-picture.html')

@login_required
def update_picture(request, picture_id):
    picture = get_object_or_404(Picture, id=picture_id, user=request.user, is_active=True)
    if request.method == 'POST':
        form = PictureUpdateForm(request.POST, instance=picture)
        if form.is_valid():
            form.save()
            messages.success(request, 'Informações da imagem atualizadas.')
            return redirect('pictures:details-picture', picture_id=picture.id)
        else:
            messages.error(request, 'Ocorreu um erro. Verifique os dados informados.')
    else:
        form = PictureUpdateForm(instance=picture)

    return render(request, 'update-picture.html', {'picture': picture, 'form': form})

@login_required
def delete_picture(request, picture_id):
    picture = get_object_or_404(Picture, id=picture_id, user=request.user)
    if request.method == 'POST':
        picture.is_active = False
        picture.save()
        messages.success(request, 'Imagem deletada com sucesso.')
        return redirect('pictures:historic-pictures')
    return render(request, 'confirm-delete-picture.html', context={'picture': picture})

@login_required
def like_picture(request, picture_id):
    picture = get_object_or_404(Picture, id=picture_id, is_active=True)
    if request.method == 'POST':
        action = request.POST.get('action') # 'like' ou 'dislike'
        if action in ['like', 'dislike']:
            is_like = True if action == 'like' else False
            like = Like.objects.filter(picture=picture, user=request.user).first()
            
            if like:
                if like.is_like == is_like:
                    like.delete() # Remove if clicking the same again
                else:
                    like.is_like = is_like
                    like.save()
            else:
                Like.objects.create(picture=picture, user=request.user, is_like=is_like)
                
    return redirect('pictures:details-picture', picture_id=picture.id)

@login_required
def comment_picture(request, picture_id):
    picture = get_object_or_404(Picture, id=picture_id, is_active=True)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                picture=picture,
                user=request.user,
                content=content
            )
            messages.success(request, 'Comentário adicionado.')
    return redirect('pictures:details-picture', picture_id=picture.id)

@login_required
def reply_comment(request, comment_id):
    parent_comment = get_object_or_404(Comment, id=comment_id)
    picture = parent_comment.picture
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                picture=picture,
                user=request.user,
                parent=parent_comment,
                content=content
            )
            messages.success(request, 'Resposta adicionada.')
    return redirect('pictures:details-picture', picture_id=picture.id)

@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    picture = comment.picture
    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ['like', 'dislike']:
            is_like = True if action == 'like' else False
            like = Like.objects.filter(comment=comment, user=request.user).first()
            
            if like:
                if like.is_like == is_like:
                    like.delete()
                else:
                    like.is_like = is_like
                    like.save()
            else:
                Like.objects.create(comment=comment, user=request.user, is_like=is_like)
                
    return redirect('pictures:details-picture', picture_id=picture.id)