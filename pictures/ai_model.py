"""
AI Models para detecção de imagens e assistência ao usuário
Suporta análise de frequência e Transformers
"""

import os
import logging
import numpy as np
from PIL import Image
import io

logger = logging.getLogger(__name__)

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Cache global dos modelos
_cache = {
    'image_classifier': None,
    'chatbot': None,
}


class AIModelManager:
    """Gerenciador de modelos de IA"""
    
    @staticmethod
    def is_low_capacity():
        """Verifica se está em ambiente de baixa capacidade"""
        try:
            import psutil
            # Se menos de 2GB de RAM disponível
            return psutil.virtual_memory().available < 2e9
        except:
            return False
    
    @staticmethod
    def detect_fake_image(image_data):
        """
        Detecta se uma imagem é real ou fake/deepfake
        Usa análise de frequência FFT
        
        Returns:
            {
                'is_fake': bool,
                'confidence': float (0-1),
                'message': str,
                'recommendation': str
            }
        """
        try:
            # Converter para PIL Image se necessário
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            else:
                image = image_data
            
            # Converter para escala de cinza
            image_gray = image.convert("L")
            image_array = np.array(image_gray)
            
            # Análise de frequência FFT
            fft = np.fft.fft2(image_array)
            magnitude = np.abs(np.fft.fftshift(fft))
            
            # Log para escala
            log_magnitude = np.log1p(magnitude)
            
            # Calcular características de frequência
            center = log_magnitude.shape[0] // 2
            radius_size = center // 4
            
            # Região central (baixa frequência)
            y_start, y_end = max(0, center - radius_size), min(log_magnitude.shape[0], center + radius_size)
            x_start, x_end = max(0, center - radius_size), min(log_magnitude.shape[1], center + radius_size)
            
            low_freq = np.sum(log_magnitude[y_start:y_end, x_start:x_end])
            total_freq = np.sum(log_magnitude)
            high_freq = total_freq - low_freq
            
            # Razão de contraste
            ratio = high_freq / (low_freq + 1e-8)
            
            # Limiar para detecção
            # Imagens geradas por IA tendem a ter menos variação de frequência
            threshold = 0.5
            is_fake_detected = ratio < threshold
            
            # Calcular confiança
            if is_fake_detected:
                confidence = min(1.0, (threshold - ratio) / threshold * 0.8 + 0.2)
            else:
                confidence = min(1.0, (ratio - threshold) / threshold * 0.8 + 0.2)
            
            if is_fake_detected:
                return {
                    'is_fake': True,
                    'confidence': confidence,
                    'message': f'⚠️ Imagem possivelmente MANIPULADA (confiança: {confidence*100:.1f}%)',
                    'recommendation': 'Esta imagem pode ter sido editada ou gerada. Verifique a origem antes de compartilhar.',
                    'score': confidence
                }
            else:
                return {
                    'is_fake': False,
                    'confidence': confidence,
                    'message': f'✅ Imagem parece AUTÊNTICA (confiança: {confidence*100:.1f}%)',
                    'recommendation': 'Esta imagem parece ser genuína.',
                    'score': confidence
                }
            
        except Exception as e:
            logger.error(f"Erro na detecção de deepfake: {e}")
            return {
                'is_fake': None,
                'confidence': 0.0,
                'message': f'⚠️ Não foi possível verificar a imagem: {str(e)}',
                'recommendation': 'Sistema de verificação temporariamente indisponível. Prossiga com cautela.',
                'score': 0.0
            }
    
    @staticmethod
    def load_image_classifier():
        """Carrega classificador de imagens para categorização"""
        if _cache['image_classifier'] is not None:
            return _cache['image_classifier']
        
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Transformers não disponível")
            return None
        
        try:
            # CLIP para classificação zero-shot (versão lite)
            device = "cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"
            classifier = pipeline(
                "zero-shot-image-classification",
                model="openai/clip-vit-base-patch16",
                device=device
            )
            _cache['image_classifier'] = classifier
            logger.info("Classificador de imagens carregado")
            return classifier
        except Exception as e:
            logger.error(f"Erro ao carregar classificador: {e}")
            return None
    
    @staticmethod
    def classify_image(image_data, labels=None):
        """
        Classifica imagem por categoria
        
        Args:
            image_data: PIL Image ou bytes
            labels: Lista de labels para classificação
        
        Returns:
            Lista de dicts com {label, score}
        """
        if labels is None:
            labels = [
                'poluição ambiental',
                'natureza limpa',
                'área urbana',
                'floresta',
                'rio ou corpo de água',
                'lixo ou resíduo',
                'pessoa',
                'animal'
            ]
        
        try:
            classifier = AIModelManager.load_image_classifier()
            if not classifier:
                # Fallback: retornar label padrão
                return [{'label': labels[0], 'score': 0.5}]
            
            # Converter para PIL Image se necessário
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            else:
                image = image_data
            
            results = classifier(image, labels, timeout=30)
            return results
        except Exception as e:
            logger.error(f"Erro na classificação: {e}")
            # Retornar resultado padrão em caso de erro
            return [{'label': labels[0], 'score': 0.5}]
    
    @staticmethod
    def load_chatbot():
        """Carrega modelo de chatbot com Transformers"""
        if _cache['chatbot'] is not None:
            return _cache['chatbot']
        
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Transformers não disponível para chatbot")
            return None
        
        try:
            # Usar modelo conversacional
            device = "cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"
            chatbot = pipeline(
                "text2text-generation",
                model="google/flan-t5-small",
                device=device
            )
            _cache['chatbot'] = chatbot
            logger.info("Chatbot carregado")
            return chatbot
        except Exception as e:
            logger.error(f"Erro ao carregar chatbot: {e}")
            return None
    
    @staticmethod
    def chat(message, context=None):
        """
        Gera resposta do chatbot
        
        Args:
            message: Mensagem do usuário em português
            context: Contexto anterior (opcional)
        
        Returns:
            str: Resposta gerada
        """
        try:
            chatbot = AIModelManager.load_chatbot()
            if not chatbot:
                return "Desculpe, o assistente não está disponível no momento."
            
            # Formatar prompt
            if context:
                prompt = f"{context}\nPergunta: {message}"
            else:
                prompt = f"Responda em português de forma concisa:\n{message}"
            
            response = chatbot(prompt, max_length=150, num_beams=4)
            
            if response and isinstance(response, list) and len(response) > 0:
                return response[0].get('generated_text', 'Desculpe, não consegui gerar uma resposta.')
            return "Desculpe, não consegui gerar uma resposta."
        except Exception as e:
            logger.error(f"Erro no chatbot: {e}")
            return f"Desculpe, não consegui processar sua mensagem."


# Funções de conveniência
def verify_image(image_data):
    """Verifica se uma imagem é real ou fake"""
    return AIModelManager.detect_fake_image(image_data)


def classify_image_pollution(image_data):
    """Classifica imagem relacionada a poluição"""
    labels = [
        'poluição terrestre',
        'poluição aérea',
        'poluição aquática',
        'natureza limpa',
        'lixo',
        'resíduo industrial',
        'rio',
        'floresta'
    ]
    return AIModelManager.classify_image(image_data, labels)


def get_chatbot_response(message):
    """Obtém resposta do chatbot"""
    return AIModelManager.chat(message)
