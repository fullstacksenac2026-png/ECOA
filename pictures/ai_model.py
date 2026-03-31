"""
AI Models para detecção de imagens e assistência ao usuário
Suporta análise de dataset, Transformers, detecção de deepfake e reconhecimento facial
"""

import os
import logging
import numpy as np
from PIL import Image
import io
import cv2
import hashlib
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)

# Deferred imports to save memory in production
TORCH_AVAILABLE = False
TRANSFORMERS_AVAILABLE = False
MEDIAPIPE_AVAILABLE = False
DLIB_AVAILABLE = False
FACE_RECOGNITION_AVAILABLE = False
MP_AVAILABLE = False


def _ensure_torch():
    global TORCH_AVAILABLE, torch, nn, transforms, resnet50
    if TORCH_AVAILABLE: return True
    try:
        import torch
        import torch.nn as nn
        import torchvision.transforms as transforms
        from torchvision.models import resnet50
        TORCH_AVAILABLE = True
        return True
    except ImportError:
        return False

def _ensure_transformers():
    global TRANSFORMERS_AVAILABLE, pipeline
    if TRANSFORMERS_AVAILABLE: return True
    try:
        from transformers import pipeline
        TRANSFORMERS_AVAILABLE = True
        return True
    except ImportError:
        return False


def _ensure_mediapipe():
    global MEDIAPIPE_AVAILABLE, MP_AVAILABLE, mp
    if MEDIAPIPE_AVAILABLE: return True
    try:
        import mediapipe as mp
        MEDIAPIPE_AVAILABLE = True
        MP_AVAILABLE = True
        return True
    except ImportError:
        return False

def _ensure_face_recognition():
    global FACE_RECOGNITION_AVAILABLE, face_recognition, sklearn, RandomForestClassifier
    if FACE_RECOGNITION_AVAILABLE: return True
    try:
        import face_recognition
        import sklearn
        from sklearn.ensemble import RandomForestClassifier
        FACE_RECOGNITION_AVAILABLE = True
        return True
    except ImportError:
        return False


# Fallback logic moved to ensures

# Cache global dos modelos
_cache = {
    'image_classifier': None,
    'chatbot': None,
    'deepfake_detector': None,
    'face_detector': None,
    'face_recognizer': None,
    'kaggle_model': None,
}


class FaceRecognitionManager:
    """Gerenciador de reconhecimento facial usando OpenFace/MediaPipe e validação com dataset Kaggle"""
    
    @staticmethod
    def load_openface_model():
        """Carrega o modelo OpenFace para reconhecimento facial"""
        if _ensure_face_recognition():
            try:
                import face_recognition
                # O face_recognition já usa OpenFace por padrão
                return face_recognition
            except Exception as e:
                logger.error(f"Erro ao carregar modelo OpenFace: {e}")
                return None
        elif _ensure_mediapipe():
            try:
                import mediapipe as mp
                # Fallback para MediaPipe
                mp_face_detection = mp.solutions.face_detection
                return mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)
            except Exception as e:
                logger.error(f"Erro ao carregar MediaPipe: {e}")
                return None
        else:
            logger.warning("Nem face_recognition nem MediaPipe disponíveis")
            return None
    
    @staticmethod
    def load_kaggle_model():
        """Carrega modelo treinado com dataset Kaggle para detecção de deepfakes"""
        # Modelo Kaggle agora usa scikit-learn (RandomForest), sem necessidade de TF
        
        if _cache.get('kaggle_model') is not None:
            return _cache['kaggle_model']
            
        try:
            import joblib
            model_path = os.path.join(os.path.dirname(__file__), 'kaggle_trained_model.pkl')
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                _cache['kaggle_model'] = model
                return model
            else:
                logger.warning("Arquivo kaggle_trained_model.pkl não encontrado.")
                return None
        except Exception as e:
            logger.error(f"Erro ao carregar modelo Kaggle: {e}")
            return None

    
    @staticmethod
    def extract_face_features(image):
        """Extrai features faciais usando OpenFace ou MediaPipe"""
        if _ensure_face_recognition():
            try:
                import face_recognition
                # Usar face_recognition (OpenFace)
                # Converter PIL para numpy array
                if isinstance(image, Image.Image):
                    image_array = np.array(image)
                else:
                    image_array = image
                
                # Detectar faces
                face_locations = face_recognition.face_locations(image_array)
                if not face_locations:
                    return None
                
                # Extrair encodings faciais (128-d features do OpenFace)
                face_encodings = face_recognition.face_encodings(image_array, face_locations)
                if not face_encodings:
                    return None
                
                return face_encodings[0]  # Retorna features da primeira face
                
            except Exception as e:
                logger.error(f"Erro ao extrair features com face_recognition: {e}")
                return None
                
        elif MP_AVAILABLE:
            try:
                # Fallback para MediaPipe
                model = FaceRecognitionManager.load_openface_model()
                if model is None:
                    return None
                
                # Converter PIL para numpy array
                if isinstance(image, Image.Image):
                    image_array = np.array(image)
                else:
                    image_array = image
                
                # Processar com MediaPipe
                results = model.process(image_array)
                
                if not results.detections:
                    return None
                
                # Usar bounding box e score de confiança como features simplificadas
                detection = results.detections[0]
                bbox = detection.location_data.relative_bounding_box
                
                # Criar features básicas baseadas na detecção
                features = np.array([
                    bbox.xmin, bbox.ymin, bbox.width, bbox.height,
                    detection.score[0],  # confiança da detecção
                    # Adicionar mais features baseadas em landmarks se disponíveis
                ])
                
                return features
                
            except Exception as e:
                logger.error(f"Erro ao extrair features com MediaPipe: {e}")
                return None
        else:
            logger.warning("Nenhuma biblioteca de reconhecimento facial disponível")
            return None
    
    @staticmethod
    def validate_with_kaggle_model(face_features):
        """Valida features faciais com modelo treinado no Kaggle"""
        if face_features is None:
            return 0.5  # Neutro se não conseguiu extrair features
            
        try:
            model = FaceRecognitionManager.load_kaggle_model()
            if model is None:
                return 0.5
            
            # Garantir formato (1, 128) para o modelo. 
            # (OpenFace já provê 128 dimensões, MediaPipe provê menos e será feito o padding).
            features = np.array(face_features).astype(float).flatten()
            if len(features) < 128:
                features = np.pad(features, (0, 128 - len(features)))
            elif len(features) > 128:
                features = features[:128]
                
            features = features.reshape(1, -1)
            
            # O modelo retorna as probabilidades para [Real, Fake] na ordem
            proba = model.predict_proba(features)[0]
            fake_prob = proba[1]  # Probabilidade de ser Fake (classe 1)
            
            return fake_prob
            
        except Exception as e:
            logger.error(f"Erro na validação Kaggle: {e}")
            return 0.5


class AIModelManager:
    """Gerenciador de modelos de IA com detecção avançada de deepfake"""
    
    @staticmethod
    def is_low_capacity():
        """Verifica se está em ambiente de baixa capacidade"""
        try:
            import psutil
            # Se menos de 1GB de RAM total (Render Free tem 512MB)
            return psutil.virtual_memory().total < 1e9
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
            
            # ========== MÉTODO 5: Reconhecimento Facial com OpenFace ==========
            face_recognition_score = AIModelManager._face_recognition_analysis(image)
            if face_recognition_score is not None:
                scores.append(('Face Recognition', face_recognition_score))
            
            # Calcular score final (média ponderada)
            weights = {'FFT': 0.20, 'Face Detection': 0.25, 'Lighting': 0.20, 'Artifacts': 0.15, 'Face Recognition': 0.20}
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
        if not _ensure_mediapipe():
            return None
        
        try:
            import mediapipe as mp
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
    def _face_recognition_analysis(image):
        """Análise de reconhecimento facial usando OpenFace e validação Kaggle"""
        try:
            # Extrair features faciais
            face_features = FaceRecognitionManager.extract_face_features(image)
            if face_features is None:
                return None  # Não conseguiu detectar face
            
            # Validar com modelo Kaggle
            kaggle_score = FaceRecognitionManager.validate_with_kaggle_model(face_features)
            
            # Análise adicional: verificar qualidade dos features
            feature_std = np.std(face_features)
            feature_mean = np.mean(face_features)
            
            # Deepfakes tendem a ter features menos variadas ou mais artificiais
            # Score baseado na qualidade: mais variância = mais provável real
            quality_score = min(1.0, max(0.0, feature_std / 0.3))
            
            # Combinar scores: Kaggle validation + quality analysis
            combined_score = (kaggle_score * 0.7) + (quality_score * 0.3)
            
            return combined_score
            
        except Exception as e:
            logger.error(f"Erro em face recognition analysis: {e}")
            return None
    
    @staticmethod
    def load_image_classifier():
        """Carrega classificador de imagens para categorização"""
        if _cache['image_classifier'] is not None:
            return _cache['image_classifier']
        
        if not _ensure_transformers():
            logger.warning("Transformers não disponível")
            return None
        
        if AIModelManager.is_low_capacity():
            logger.warning("Ambiente de baixa capacidade detectado. Ignorando carregamento do classificador pesado.")
            return None
        
        try:
            # CLIP para classificação zero-shot (versão lite)
            device = "cuda" if _ensure_torch() and torch.cuda.is_available() else "cpu"
            from transformers import pipeline
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
        
        if not _ensure_transformers():
            logger.warning("Transformers não disponível para chatbot")
            return None

        if AIModelManager.is_low_capacity():
            logger.warning("Ambiente de baixa capacidade detectado. Ignorando carregamento do chatbot pesado.")
            return None
        
        try:
            # Usar modelo conversacional
            if not _ensure_transformers():
                return None
            
            device = "cuda" if _ensure_torch() and torch.cuda.is_available() else "cpu"
            from transformers import pipeline
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
