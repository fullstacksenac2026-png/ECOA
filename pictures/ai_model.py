"""
AI Models para detecção de imagens e assistência ao usuário
Suporta análise de dataset, Transformers e detecção de deepfake
"""

import os
import logging
import numpy as np
from PIL import Image
import io
import cv2

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

try:
    import tensorflow as tf
    from tensorflow.keras.applications import EfficientNetB0
    from tensorflow.keras.preprocessing import image as keras_image
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

# Cache global dos modelos
_cache = {
    'image_classifier': None,
    'chatbot': None,
    'deepfake_detector': None,
    'face_detector': None,
}


class AIModelManager:
    """Gerenciador de modelos de IA com detecção avançada de deepfake"""
    
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
        Detecta se uma imagem é real ou fake/deepfake usando múltiplas técnicas
        
        Métodos utilizados:
        1. Análise de frequência FFT (artefatos de compressão)
        2. Detecção de faces com MediaPipe
        3. Análise de consistência de iluminação
        4. Detecção de artefatos de compressão JPEG
        
        Returns:
            {
                'is_fake': bool,
                'confidence': float (0-1),
                'message': str,
                'recommendation': str,
                'methods': list de métodos usados e scores
            }
        """
        try:
            # Converter para PIL Image se necessário
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            else:
                image = image_data
            
            # Converter para RGB se necessário
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Inicializar scores
            scores = []
            
            # ========== MÉTODO 1: Análise de Frequência FFT ==========
            fft_score = AIModelManager._fft_analysis(image)
            scores.append(('FFT', fft_score))
            
            # ========== MÉTODO 2: Detecção de Faces ==========
            face_score = AIModelManager._face_consistency_check(image)
            if face_score is not None:
                scores.append(('Face Detection', face_score))
            
            # ========== MÉTODO 3: Análise de Iluminação ==========
            lighting_score = AIModelManager._lighting_consistency(image)
            scores.append(('Lighting', lighting_score))
            
            # ========== MÉTODO 4: Compressão e Artefatos ==========
            artifact_score = AIModelManager._compression_artifacts(image)
            scores.append(('Artifacts', artifact_score))
            
            # Calcular score final (média ponderada)
            weights = {'FFT': 0.25, 'Face Detection': 0.30, 'Lighting': 0.25, 'Artifacts': 0.20}
            total_score = 0
            total_weight = 0
            
            for method, score in scores:
                weight = weights.get(method, 0.2)
                total_score += score * weight
                total_weight += weight
            
            final_confidence = total_score / total_weight if total_weight > 0 else 0.5
            
            # Classificação: score > 0.6 = potencialmente fake
            is_fake = final_confidence > 0.6
            
            if is_fake:
                return {
                    'is_fake': True,
                    'confidence': final_confidence,
                    'message': f'⚠️ Imagem possivelmente MANIPULADA (confiança: {final_confidence*100:.1f}%)',
                    'recommendation': 'Esta imagem pode ter sido editada, gerada por IA ou deepfake. Verifique a origem antes de compartilhar.',
                    'score': final_confidence,
                    'methods': [{'name': m, 'score': s} for m, s in scores]
                }
            else:
                return {
                    'is_fake': False,
                    'confidence': 1 - final_confidence,
                    'message': f'✅ Imagem parece AUTÊNTICA (confiança: {(1-final_confidence)*100:.1f}%)',
                    'recommendation': 'Esta imagem parece ser genuína.',
                    'score': 1 - final_confidence,
                    'methods': [{'name': m, 'score': s} for m, s in scores]
                }
            
        except Exception as e:
            logger.error(f"Erro na detecção de deepfake: {e}")
            return {
                'is_fake': None,
                'confidence': 0.0,
                'message': f'⚠️ Não foi possível verificar a imagem: {str(e)}',
                'recommendation': 'Sistema de verificação temporariamente indisponível. Prossida com cautela.',
                'score': 0.0,
                'methods': []
            }
    
    @staticmethod
    def _fft_analysis(image):
        """Análise de frequência para detectar artefatos de compressão"""
        try:
            image_gray = image.convert("L")
            image_array = np.array(image_gray)
            
            # Aplicar FFT
            fft = np.fft.fft2(image_array)
            magnitude = np.abs(np.fft.fftshift(fft))
            log_magnitude = np.log1p(magnitude)
            
            # Calcular características de frequência
            center = log_magnitude.shape[0] // 2
            radius_size = center // 4
            
            y_start = max(0, center - radius_size)
            y_end = min(log_magnitude.shape[0], center + radius_size)
            x_start = max(0, center - radius_size)
            x_end = min(log_magnitude.shape[1], center + radius_size)
            
            low_freq = np.sum(log_magnitude[y_start:y_end, x_start:x_end])
            total_freq = np.sum(log_magnitude)
            high_freq = total_freq - low_freq
            
            ratio = high_freq / (low_freq + 1e-8)
            
            # Imagens geradas por IA tendem a ter menos variação de frequência
            # Normalizamos o score [0, 1] onde 1 = provavelmente fake
            fft_score = 1.0 / (1.0 + np.exp(-(ratio - 0.5) * 5))
            return fft_score
        except Exception as e:
            logger.error(f"Erro em FFT analysis: {e}")
            return 0.5
    
    @staticmethod
    def _face_consistency_check(image):
        """Verifica consistência de faces usando MediaPipe"""
        if not MEDIAPIPE_AVAILABLE:
            return None
        
        try:
            mp_face_detection = mp.solutions.face_detection
            
            # Converter PIL para array numpy
            image_array = np.array(image)
            
            with mp_face_detection.FaceDetection(
                model_selection=1,
                min_detection_confidence=0.5
            ) as face_detection:
                results = face_detection.process(image_array)
                
                if not results.detections:
                    # Sem faces detectadas = indício de imagem artificial
                    return 0.4
                
                # Analisar consistência das faces detectadas
                detections = results.detections
                scores_list = []
                
                for detection in detections:
                    # Score de confiança original do MediaPipe
                    confidence = detection.location_data.relative_bounding_box.width
                    scores_list.append(confidence)
                
                # Se todas as faces têm alta confiança = mais provavelmente real
                avg_confidence = np.mean(scores_list) if scores_list else 0.5
                
                # Inversão: alta confiança = score baixo (real)
                face_score = 1.0 - avg_confidence
                return face_score
        except Exception as e:
            logger.error(f"Erro em face detection: {e}")
            return None
    
    @staticmethod
    def _lighting_consistency(image):
        """Verifica consistência de iluminação"""
        try:
            image_array = np.array(image)
            
            # Dividir em canais
            r, g, b = cv2.split(image_array)
            
            # Calcular variância de iluminação em diferentes regiões
            h, w = r.shape
            regions = []
            
            for i in range(4):
                for j in range(4):
                    y_start = i * h // 4
                    y_end = (i + 1) * h // 4
                    x_start = j * w // 4
                    x_end = (j + 1) * w // 4
                    
                    region = r[y_start:y_end, x_start:x_end]
                    regions.append(np.var(region))
            
            # Desvio padrão da variância entre regiões
            consistency = np.std(regions) / (np.mean(regions) + 1e-8)
            
            # Normalizar: imagens geradas tendem ter iluminação mais consistente
            lighting_score = 1.0 / (1.0 + np.exp(-(consistency - 1.0) * 2))
            return lighting_score
        except Exception as e:
            logger.error(f"Erro em lighting check: {e}")
            return 0.5
    
    @staticmethod
    def _compression_artifacts(image):
        """Detecta artefatos de compressão JPEG"""
        try:
            image_array = np.array(image)
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            
            # Aplicar transformada discreta de cossenos (DCT) para detectar blocos JPEG
            dct = cv2.dct(np.float32(gray) / 255.0)
            
            # Quantizar para detectar padrões de quantização JPEG
            dct_quantized = np.round(dct * 8) / 8
            
            # Diferença entre DCT e quantização
            quantization_error = np.sum(np.abs(dct - dct_quantized))
            
            # Normalizar em relação ao tamanho
            normalized_error = quantization_error / (gray.size + 1e-8)
            
            # Higher error = mais compressão = mais provavelmente real (não gerado)
            artifact_score = 1.0 / (1.0 + np.exp(normalized_error * 10))
            return artifact_score
        except Exception as e:
            logger.error(f"Erro em compression artifacts: {e}")
            return 0.5
    
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
