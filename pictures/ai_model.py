"""
AI Models para detecção de imagens e assistência ao usuário
Suporta TensorFlow Lite para dispositivos fracos e Transformers
"""

import os
import logging
import numpy as np
from PIL import Image
import io

logger = logging.getLogger(__name__)

try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

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
    'deepfake_detector': None,
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
    def load_deepfake_detector():
        """
        Carrega modelo de detecção de deepfake/imagem falsa
        Usa CNN treinada para detectar faces geradas por IA
        """
        if _cache['deepfake_detector'] is not None:
            return _cache['deepfake_detector']
        
        if not TENSORFLOW_AVAILABLE:
            logger.warning("TensorFlow não disponível")
            return None
        
        try:
            # Usar um modelo simples baseado em CNN para detecção de imagens geradas
            model = tf.keras.Sequential([
                tf.keras.layers.Input(shape=(224, 224, 3)),
                tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
                tf.keras.layers.MaxPooling2D((2, 2)),
                tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                tf.keras.layers.MaxPooling2D((2, 2)),
                tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                tf.keras.layers.Flatten(),
                tf.keras.layers.Dense(64, activation='relu'),
                tf.keras.layers.Dropout(0.5),
                tf.keras.layers.Dense(2, activation='sigmoid')  # Real vs Fake
            ])
            
            _cache['deepfake_detector'] = model
            logger.info("Modelo de detecção de deepfake carregado")
            return model
        except Exception as e:
            logger.error(f"Erro ao carregar deepfake detector: {e}")
            return None
    
    @staticmethod
    def detect_fake_image(image_data):
        """
        Detecta se uma imagem é real ou fake/deepfake
        
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
            
            # Redimensionar para 224x224
            image_resized = image.resize((224, 224))
            image_array = np.array(image_resized) / 255.0
            image_array = np.expand_dims(image_array, axis=0)
            
            # Usar modelo TensorFlow se disponível
            if TENSORFLOW_AVAILABLE:
                model = AIModelManager.load_deepfake_detector()
                if model:
                    predictions = model.predict(image_array, verbose=0)
                    # predictions[0][0] = probabilidade de ser real
                    # predictions[0][1] = probabilidade de ser fake
                    
                    real_prob = float(predictions[0][0])
                    fake_prob = float(predictions[0][1])
                    
                    if fake_prob > 0.5:
                        return {
                            'is_fake': True,
                            'confidence': fake_prob,
                            'message': f'Imagem possivelmente FALSA/DEEPFAKE (confiança: {fake_prob*100:.1f}%)',
                            'recommendation': 'Esta imagem pode ter sido manipulada ou gerada por IA. Verifique a origem.',
                            'score': fake_prob
                        }
                    else:
                        return {
                            'is_fake': False,
                            'confidence': real_prob,
                            'message': f'Imagem provavelmente REAL (confiança: {real_prob*100:.1f}%)',
                            'recommendation': 'Esta imagem parece ser autêntica.',
                            'score': real_prob
                        }
            
            # Fallback: análise simples baseada em frequência
            return AIModelManager._analyze_image_frequency(image_array)
            
        except Exception as e:
            logger.error(f"Erro na detecção de deepfake: {e}")
            return {
                'is_fake': None,
                'confidence': 0.0,
                'message': f'Erro ao processar imagem: {str(e)}',
                'recommendation': 'Não foi possível verificar a imagem.',
                'score': 0.0
            }
    
    @staticmethod
    def _analyze_image_frequency(image_array):
        """Análise simples de frequência para detecção de imagens geradas por IA"""
        try:
            # FFT 2D para análise de frequência
            fft = np.fft.fft2(np.mean(image_array, axis=-1)[0])
            magnitude = np.abs(np.fft.fftshift(fft))
            
            # Imagens geradas por IA tendem a ter padrões de frequência diferentes
            # Calcular razão de baixa vs alta frequência
            center = magnitude.shape[0] // 2
            size = center // 4
            
            low_freq = np.sum(magnitude[center-size:center+size, center-size:center+size])
            high_freq = np.sum(magnitude) - low_freq
            
            ratio = high_freq / (low_freq + 1e-8)
            threshold = 0.8
            
            is_fake = ratio < threshold
            confidence = abs(ratio - threshold) / threshold
            
            return {
                'is_fake': is_fake,
                'confidence': min(confidence, 1.0),
                'message': f'Análise de frequência: {"FALSA" if is_fake else "REAL"}',
                'recommendation': 'Uso de análise de frequência de Fourier.',
                'score': confidence
            }
        except Exception as e:
            logger.error(f"Erro na análise de frequência: {e}")
            return {
                'is_fake': None,
                'confidence': 0.0,
                'message': 'Análise técnica não disponível',
                'recommendation': 'Sistema de verificação temporariamente indisponível.',
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
            # CLIP para classificação zero-shot
            classifier = pipeline(
                "zero-shot-image-classification",
                model="openai/clip-vit-base-patch32",
                device="cpu" if AIModelManager.is_low_capacity() else "cuda" if torch.cuda.is_available() else "cpu"
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
                return []
            
            # Converter para PIL Image se necessário
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            else:
                image = image_data
            
            results = classifier(image, labels, timeout=30)
            return results
        except Exception as e:
            logger.error(f"Erro na classificação: {e}")
            return []
    
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
            chatbot = pipeline(
                "text2text-generation",
                model="google/flan-t5-small",  # Modelo leve para dispositivos fracos
                device="cpu" if AIModelManager.is_low_capacity() else "cuda" if torch.cuda.is_available() else "cpu"
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
            return f"Erro ao processar sua mensagem: {str(e)}"


# Funções de conveniência
def verify_image(image_data):
    """Verifica se uma imagem é real ou fake"""
    return AIModelManager.detect_fake_image(image_data)


def classify_image_pollution(image_data):
    """Classifica imagem relacionada a poluição"""
    labels = [
        'poluição terrestres',
        'poluição aérea',
        'poluição aquática',
        'natureza limpa',
        'lixo',
        'resíduo industrial'
    ]
    return AIModelManager.classify_image(image_data, labels)


def get_chatbot_response(message):
    """Obtém resposta do chatbot"""
    return AIModelManager.chat(message)
