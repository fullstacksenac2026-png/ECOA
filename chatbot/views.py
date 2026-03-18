from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
import json
import logging

from .models import ChatSession, ChatMessage
from .forms import ChatMessageForm, ChatSessionForm
from pictures.ai_model import get_chatbot_response

logger = logging.getLogger(__name__)


@login_required
def chatbot_list(request):
    """Lista todas as sessões de chat do usuário"""
    sessions = request.user.chat_sessions.filter(is_active=True).order_by('-updated_at')
    
    # Paginação
    paginator = Paginator(sessions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'sessions': page_obj.object_list,
    }
    return render(request, 'chatbot/chat_list.html', context)


@login_required
def create_chat(request):
    """Cria uma nova sessão de chat"""
    if request.method == 'POST':
        form = ChatSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.user = request.user
            session.save()
            
            # Mensagem de boas-vindas
            ChatMessage.objects.create(
                session=session,
                role='assistant',
                content='Olá! Sou um assistente de IA. Como posso ajudar você hoje?\n\n'
                        'Posso responder dúvidas sobre:\n'
                        '• Poluição ambiental e sua denúncia\n'
                        '• Legislação ambiental\n'
                        '• Métodos de descarte correto\n'
                        '• E muito mais!\n\n'
                        'O que você gostaria de saber?'
            )
            
            messages.success(request, 'Nova conversa iniciada!')
            return redirect('chatbot:detail', session_id=session.id)
    else:
        form = ChatSessionForm()
    
    return render(request, 'chatbot/create_chat.html', {'form': form})


@login_required
def chat_detail(request, session_id):
    """Exibe uma sessão de chat com todas as mensagens"""
    session = get_object_or_404(ChatSession, id=session_id, user=request.user, is_active=True)
    
    # Obter todas as mensagens
    messages_list = session.messages.all().order_by('created_at')
    
    # Paginação opcional
    paginator = Paginator(messages_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    form = ChatMessageForm()
    
    context = {
        'session': session,
        'page_obj': page_obj,
        'messages': page_obj.object_list,
        'form': form,
    }
    return render(request, 'chatbot/chat_detail.html', context)


@login_required
@require_http_methods(["POST"])
def send_message(request, session_id):
    """Envia uma mensagem e obtém resposta da IA (view tradicional, redireciona)"""
    session = get_object_or_404(ChatSession, id=session_id, user=request.user, is_active=True)
    
    form = ChatMessageForm(request.POST)
    if form.is_valid():
        # Salvar mensagem do usuário
        user_message = form.save(commit=False)
        user_message.session = session
        user_message.role = 'user'
        user_message.save()
        
        # Gerar resposta da IA
        try:
            # Obter contexto das mensagens anteriores
            context = '\n'.join([
                f"{msg.get_role_display()}: {msg.content}"
                for msg in session.messages.all().order_by('created_at')[:-5:]
            ]) if session.messages.count() > 1 else None
            
            ai_response = get_chatbot_response(user_message.content)
            
            # Salvar resposta da IA
            ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=ai_response
            )
            
            # Atualizar título se ainda for 'Nova Conversa'
            if session.title == 'Nova Conversa':
                session.title = user_message.content[:50]
                session.save()
            
            messages.success(request, 'Mensagem enviada!')
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            messages.error(request, 'Erro ao processar sua mensagem. Tente novamente.')
    else:
        messages.error(request, 'Erro ao salvar mensagem.')
    
    return redirect('chatbot:detail', session_id=session_id)


@login_required
@require_http_methods(["POST"])
def api_send_message(request):
    """
    API endpoint para enviar mensanges
    Retorna a resposta em JSON (para requisições AJAX)
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        message_content = data.get('message', '').strip()
        
        if not message_content:
            return JsonResponse({'error': 'Mensagem vazia'}, status=400)
        
        session = get_object_or_404(ChatSession, id=session_id, user=request.user, is_active=True)
        
        # Salvar mensagem do usuário
        user_message = ChatMessage.objects.create(
            session=session,
            role='user',
            content=message_content
        )
        
        # Gerar resposta da IA
        try:
            ai_response = get_chatbot_response(message_content)
            
            # Salvar resposta
            assistant_message = ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=ai_response
            )
            
            # Atualizar título
            if session.title == 'Nova Conversa':
                session.title = message_content[:50]
                session.save()
            
            return JsonResponse({
                'success': True,
                'user_message': {
                    'id': user_message.id,
                    'content': user_message.content,
                    'role': user_message.role,
                },
                'assistant_message': {
                    'id': assistant_message.id,
                    'content': assistant_message.content,
                    'role': assistant_message.role,
                }
            })
        except Exception as e:
            logger.error(f"Erro na IA: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Erro ao processar: {str(e)}'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Erro ao processar requisição: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def delete_chat(request, session_id):
    """Deleta uma sessão de chat (soft delete)"""
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    
    if request.method == 'POST':
        session.is_active = False
        session.save()
        messages.success(request, 'Conversa deletada.')
        return redirect('chatbot:list')
    
    return render(request, 'chatbot/confirm_delete.html', {'session': session})
