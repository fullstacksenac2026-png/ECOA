from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.db.models import Q, Count
from .models import Picture, Complaint, Geolocation, Verify, TITLE_COMPLAINT_CHOICES, Comment, Like
from .forms import ComplaintForm, PictureUpdateForm
from authorization.models import User
import base64
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
import os

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

_lite_interpreter = None
_lite_labels = None

def load_lite_model():
    """Carrega o modelo TensorFlow Lite otimizado para dispositivos moveis."""
    global _lite_interpreter, _lite_labels
    
    if _lite_interpreter is not None:
        return True
    
    # Verificar se TensorFlow está disponível
    if not TENSORFLOW_AVAILABLE:
        print("TensorFlow não disponível - recurso de classificação de imagem desabilitado")
        return False
        
    try:
        # Tentar importar ai_edge_litert
        try:
            import ai_edge_litert as lite
        except ImportError:
            # Fallback para TensorFlow (para desenvolvimento)
            import tensorflow as lite
        
        # Labels para classificação de imagens (poluição, natureza, etc.)
        _lite_labels = [
            'Poluição ou lixo', 'Natureza limpa', 'Objeto aleatório', 'Pessoa',
            'Urbano', 'Rural', 'Rio ou Mar', 'Floresta', 'Área Industrial'
        ]
        
        # Tentar carregar um modelo MobileNet leve pré-treinado
        try:
            model_path = os.path.join(os.path.dirname(__file__), 'models', 'mobile_classifier.tflite')
            
            if os.path.exists(model_path):
                _lite_interpreter = lite.Interpreter(model_path=model_path)
            else:
                # Modelo não encontrado - usar classificação via TensorFlow Hub
                _lite_interpreter = 'tensorflow_hub'
                return True
        except Exception as e:
            print(f"LiteRT: Erro ao carregar modelo local: {e}")
            _lite_interpreter = 'tensorflow_hub'
            
        return True
        
    except (ImportError, Exception) as e:
        print(f"LiteRT: Erro ao inicializar: {e}")
        return False

def classify_image_lite(image, candidate_labels):
    """Classifica imagem usando AI Edge LiteRT (otimizado para mobile)."""
    global _lite_interpreter
    
    if _lite_interpreter is None:
        load_lite_model()
    
    try:
        # Redimensionar para entrada do modelo MobileNet (224x224)
        img = image.resize((224, 224))
        img_array = list(img.getdata())
        
        # Normalizar para valores entre -1 e 1 (MobileNet V2)
        input_data = [[pixel[0]/127.5 - 1, pixel[1]/127.5 - 1, pixel[2]/127.5 - 1] 
                      for pixel in img_array]
        input_data = [input_data]  # Batch dimension
        
        if _lite_interpreter == 'tensorflow_hub':
            # Fallback para TensorFlow Hub (requer conexão)
            try:
                import tensorflow_hub as hub
                model_url = "https://tfhub.dev/google/tf2-preview/mobilenet_v2/classification/4"
                model = hub.load(model_url)
                
                # Converter imagem para formato correto
                import numpy as np
                img_array = np.array(img.resize((224, 224))) / 255.0
                img_array = np.expand_dims(img_array, axis=0)
                
                predictions = model(img_array).numpy()[0]
                
                # Obter top prediction
                top_idx = np.argmax(predictions)
                score = float(predictions[top_idx])
                
                # Mapear para nossos labels (simplificado)
                # Em produção, você usaria um modelo customizado
                label = candidate_labels[0] if score > 0.5 else candidate_labels[1]
                
                return [{'label': label, 'score': min(score, 1.0)}]
                
            except ImportError:
                # TensorFlow Hub não disponível
                return [{'label': candidate_labels[0], 'score': 0.0}]
        
        # Usar interpreter TFLite
        interpreter = _lite_interpreter
        interpreter.allocate_tensors()
        
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        # Converter para array numpy
        import numpy as np
        input_data = np.array(input_data, dtype=np.float32)
        
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        
        output_data = interpreter.get_tensor(output_details[0]['index'])
        
        # Obter predição
        predictions = output_data[0]
        top_idx = np.argmax(predictions)
        
        # Retornar resultado no formato esperado
        label = candidate_labels[min(top_idx, len(candidate_labels)-1)]
        score = float(predictions[top_idx])
        
        return [{'label': label, 'score': min(score, 1.0)}]
        
    except Exception as e:
        print(f"LiteRT: Erro na classificação: {e}")
        return [{'label': candidate_labels[0], 'score': 0.0}]


_classifiers = {'full': None, 'lite': None}

def get_classifier(lite=False):
    global _classifiers
    mode = 'lite' if lite else 'full'
    
    if _classifiers[mode] is None:
        # Verificar se torch está disponível
        if not TORCH_AVAILABLE:
            print("Torch não disponível - recurso de classificação de imagem desabilitado")
            return None
            
        try:
            from transformers import pipeline
            model_name = "openai/clip-vit-base-patch32"
            
            if lite:
                # Otimizações para modo Lite - menos threads e CPU
                torch.set_num_threads(1)
                _classifiers[mode] = pipeline(
                    "zero-shot-image-classification",
                    model=model_name,
                    device="cpu"
                )
            else:
                device = "cuda" if torch.cuda.is_available() else "cpu"
                _classifiers[mode] = pipeline(
                    "zero-shot-image-classification",
                    model=model_name,
                    device=device
                )
        except (ImportError, Exception) as e:
            print(f"Erro ao carregar IA ({mode}): {e}")
            return None
    return _classifiers[mode]

def get_ai_classifier(request):

    use_lite = is_low_capacity(request)
    
    if use_lite:
        # Tentar carregar LiteRT primeiro
        if load_lite_model():
            return {'type': 'litert', 'function': classify_image_lite}
    
    # Fallback para Transformers (desktop)
    classifier = get_classifier(lite=use_lite)
    if classifier:
        return {'type': 'transformers', 'function': classifier}
    
    return None

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
            
            messages.success(request, 'Queixa registrada com sucesso.')
            return redirect('pictures:details-picture', picture_id=picture.id)
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
            image_data = image_data.split(',')[1] if ',' in image_data else image_data
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
        except Exception as e:
            messages.error(request, 'Erro ao processar a imagem.')
            return redirect('pictures:take-picture')

        buffer = BytesIO()
        # Converte para RGB se tiver transparência (JPEG não suporta RGBA)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        image_file = ContentFile(buffer.getvalue(), name=f'picture_{request.user.id}.jpg')

        # Obter classificador apropriado para o dispositivo
        ai_classifier = get_ai_classifier(request)
        is_mobile = is_low_capacity(request)
        
        is_valid = False
        detected_place = "Não identificado"
        ai_message = "IA não disponível"
        ai_type = "Nenhum"
        
        if ai_classifier:
            try:
                ai_img = image
                # Redimensionar para LiteRT (menor consumo)
                if is_mobile:
                    ai_img = image.resize((224, 224))
                
                ai_type = ai_classifier['type'].upper()
                classifier_fn = ai_classifier['function']
                
                if ai_classifier['type'] == 'litert':
                    # AI Edge LiteRT (otimizado para mobile) - não usa torch
                    valid_labels = ["Poluição ou lixo", "Natureza limpa", "Objeto aleatório", "Pessoa"]
                    v_res = classifier_fn(ai_img, valid_labels)
                    is_valid = v_res[0]['label'] == "Poluição ou lixo" and v_res[0]['score'] > 0.4
                    
                    place_labels = ["Urbano", "Rural", "Rio ou Mar", "Floresta", "Área Industrial"]
                    p_res = classifier_fn(ai_img, place_labels)
                    detected_place = p_res[0]['label']
                    
                    ai_message = f"LiteRT detectou: {detected_place}. Identificado como {'Real' if is_valid else 'Irrelevante'} ({v_res[0]['score']*100:.1f}%)"
                elif TORCH_AVAILABLE:
                    # Transformers (desktop) - requer torch
                    with torch.inference_mode():
                        valid_labels = ["Poluição ou lixo", "Natureza limpa", "Objeto aleatório", "Pessoa"]
                        v_res = classifier_fn(ai_img, candidate_labels=valid_labels)
                        is_valid = v_res[0]['label'] == "Poluição ou lixo" and v_res[0]['score'] > 0.4
                        
                        place_labels = ["Urbano", "Rural", "Rio ou Mar", "Floresta", "Área Industrial"]
                        p_res = classifier_fn(ai_img, candidate_labels=place_labels)
                        detected_place = p_res[0]['label']
                        
                        ai_message = f"IA detectou: {detected_place}. Identificado como {'Real' if is_valid else 'Irrelevante'} ({v_res[0]['score']*100:.1f}%)"
                        
            except Exception as e:
                ai_message = f"Erro na análise: {str(e)}"

        picture = Picture.objects.create(
            user=request.user,
            image=image_file,
            title="Aguardando queixa...",
            content=f"Local sugerido pela IA: {detected_place}"
        )

        if latitude and longitude:
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

        messages.info(request, f'IA ({ai_type}) analisou a foto. Agora complete as informações da sua queixa.')
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