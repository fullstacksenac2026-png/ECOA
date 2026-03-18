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
    
    # Base queryset - showing all active pictures
    pictures = Picture.objects.filter(is_active=True)
    
    if search_query:
        pictures = pictures.filter(
            models.Q(title__icontains=search_query) | 
            models.Q(content__icontains=search_query)
        )
    
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
        'search_query': search_query
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
            # Redireciona para o histórico público (feed) ao invés de apenas a foto
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
        image_file = ContentFile(buffer.getvalue(), name=f'picture_{request.user.id}.jpg')

        # Usar nova IA para análise
        is_fake = None
        ai_message = "IA não disponível"
        detected_place = "Não identificado"
        
        try:
            # Verificar se é imagem fake (deepfake detection)
            verify_result = verify_image(image)
            is_fake = verify_result['is_fake']
            ai_message = verify_result['message']
            
            # Classificar imagem (poluição, etc.)
            classifications = classify_image_pollution(image)
            if classifications:
                detected_place = classifications[0]['label']
        except Exception as e:
            logger.error(f"Erro na análise de IA: {e}")
            ai_message = f"Erro na análise: {str(e)}"

        picture = Picture.objects.create(
            user=request.user,
            image=image_file,
            title="Aguardando queixa...",
            content=f"Local: {detected_place}"
        )

        if latitude and longitude:
            Geolocation.objects.create(
                picture=picture,
                latitude=float(latitude),
                longitude=float(longitude)
            )

        Verify.objects.create(
            picture=picture,
            is_fake=is_fake if is_fake is not None else False,
            verify_message=ai_message
        )

        messages.info(request, f'Foto analisada pela IA. Complete as informações da sua queixa.')
        return redirect('pictures:create-complaint', picture_id=picture.id)

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

        # Obter classificador apropriado para o dispositivo
        ai_classifier = get_ai_classifier(request)
        is_mobile = is_low_capacity(request)
        
        is_valid = False
        detected_place = "Não identificado"
        ai_message = "IA não disponível (Upload manual)"
        ai_type = "Nenhum"
        
        if ai_classifier:
            try:
                from PIL import Image
                img = Image.open(image_file)
                if is_mobile:
                    img = img.resize((224, 224))
                
                ai_type = ai_classifier['type'].upper()
                classifier_fn = ai_classifier['function']
                
                if ai_classifier['type'] == 'litert':
                    # AI Edge LiteRT (otimizado para mobile) - não usa torch
                    valid_labels = ["Poluição ou lixo", "Natureza limpa", "Objeto aleatório", "Pessoa"]
                    v_res = classifier_fn(img, valid_labels)
                    is_valid = v_res[0]['label'] == "Poluição ou lixo" and v_res[0]['score'] > 0.4
                    
                    place_labels = ["Urbano", "Rural", "Rio ou Mar", "Floresta", "Área Industrial"]
                    p_res = classifier_fn(img, place_labels)
                    detected_place = p_res[0]['label']
                    
                    ai_message = f"LiteRT detectou: {detected_place} ({v_res[0]['score']*100:.1f}%)"
                elif TORCH_AVAILABLE:
                    # Transformers (desktop) - requer torch
                    with torch.inference_mode():
                        valid_labels = ["Poluição ou lixo", "Natureza limpa", "Objeto aleatório", "Pessoa"]
                        v_res = classifier_fn(img, candidate_labels=valid_labels)
                        is_valid = v_res[0]['label'] == "Poluição ou lixo" and v_res[0]['score'] > 0.4
                        
                        place_labels = ["Urbano", "Rural", "Rio ou Mar", "Floresta", "Área Industrial"]
                        p_res = classifier_fn(img, candidate_labels=place_labels)
                        detected_place = p_res[0]['label']
                        
                        ai_message = f"IA detectou: {detected_place} ({v_res[0]['score']*100:.1f}%)"
            except Exception:
                pass

        # Recarregar a imagem para salvar (após可能被resize)
        image_file.seek(0)
        image_data = image_file.read()
        image_file = ContentFile(image_data, name=image_file.name)

        picture = Picture.objects.create(
            user=request.user,
            image=image_file,
            title="Aguardando queixa...",
            content=f"Local sugerido pela IA: {detected_place}"
        )

        Geolocation.objects.create(
            picture=picture,
            latitude=float(latitude),
            longitude=float(longitude)
        )

        Verify.objects.create(
            picture=picture,
            is_fake=not is_valid,
            verify_message=ai_message
        )

        messages.info(request, f'IA ({ai_type}) analisou o upload. Complete sua queixa abaixo.')
        return redirect('pictures:create-complaint', picture_id=picture.id)

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