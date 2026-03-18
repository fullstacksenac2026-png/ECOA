# Guia de Implementação de IA no Projeto

## Resumo das Mudanças

Este documento descreve as novas funcionalidades de IA integradas ao projeto Django:

1. **Detecção de Deepfake/Imagens Falsas** - usando TensorFlow
2. **Classificação de Imagens** - usando Transformers (CLIP)
3. **Chatbot Assistente** - usando Transformers (FLAN-T5)
4. **APIs de IA** - endpoints para processar imagens e mensagens

---

## Requisitos

### Dependências Adicionadas

As seguintes dependências foram adicionadas ao `requirements.txt`:

```
tensorflow==2.13.0
tensorflow-hub==0.13.0
torch==2.0.1
transformers==4.35.2
opencv-python==4.8.1.78
onnx==1.14.1
onnxruntime==1.16.3
```

### Instalação

```bash
pip install -r requirements.txt
```

**Nota**: TensorFlow 2.13 é compatível com Python 3.11 a 3.13 e funciona em dispositivos com recursos limitados.

---

## 1. Detecção de Deepfake (Take Picture)

### Localização
- **Módulo**: `pictures/ai_model.py`
- **Função Principal**: `AIModelManager.detect_fake_image(image_data)`

### Como Funciona

Quando um usuário tira uma foto ou faz upload em "Take Picture":

1. A imagem é processada pela função `verify_image()`
2. O modelo analisa se é real ou fake usando CNN
3. Calcula confiança e retorna recomendação
4. Resultado é salvo no modelo `Verify` do banco

### Resposta

```json
{
    "is_fake": false,
    "confidence": 0.85,
    "message": "Imagem provavelmente REAL (confiança: 85%)",
    "recommendation": "Esta imagem parece ser autêntica.",
    "score": 0.85
}
```

### Endpoint API

```
POST /pictures/api/verify-image/
```

Params:
- `image`: base64 ou arquivo (multipart/form-data)

---

## 2. Classificação de Imagens

### Localização
- **Módulo**: `pictures/ai_model.py`
- **Função Principal**: `AIModelManager.classify_image(image_data, labels)`

### Como Funciona

Classifica imagens em categorias relacionadas a poluição:

- Poluição terrestre
- Poluição aérea
- Poluição aquática
- Natureza limpa
- Área urbana/rural
- Floresta
- etc.

### Endpoint API

```
POST /pictures/api/classify-image/
```

Resposta:

```json
{
    "success": true,
    "classifications": [
        {
            "label": "poluição ambiental",
            "score": 0.92
        },
        {
            "label": "área urbana",
            "score": 0.78
        }
    ]
}
```

---

## 3. Chatbot Assistente

### Localização
- **App**: `chatbot/`
- **URLs**: `/chatbot/`
- **Função Principal**: `AIModelManager.chat(message, context)`

### Estrutura da App Chatbot

```
chatbot/
├── models.py          # ChatSession, ChatMessage
├── views.py           # Views para gerenciar chats
├── urls.py            # Rotas do chatbot
├── forms.py           # Formulários
├── admin.py           # Interface do admin
└── templates/
    └── chatbot/
        ├── chat_list.html       # Lista de conversas
        ├── create_chat.html     # Criar nova conversa
        ├── chat_detail.html     # Detalhe da conversa
        └── confirm_delete.html  # Confirmação de exclusão
```

### Modelos de Dados

**ChatSession**
```python
class ChatSession(models.Model):
    user = ForeignKey(User)           # Usuário proprietário
    title = CharField(max_length=255) # Título da conversa
    created_at = DateTimeField()      # Criação
    updated_at = DateTimeField()      # Última atualização
    is_active = BooleanField()        # Status (soft delete)
```

**ChatMessage**
```python
class ChatMessage(models.Model):
    session = ForeignKey(ChatSession) # Sessão pai
    role = CharField()                # 'user' ou 'assistant'
    content = TextField()             # Conteúdo da mensagem
    created_at = DateTimeField()      # Timestamp
```

### URLs Disponíveis

| URL | Método | Descrição |
|-----|--------|-----------|
| `/chatbot/` | GET | Listar todas as conversas |
| `/chatbot/novo/` | GET/POST | Criar nova conversa |
| `/chatbot/sessao/<id>/` | GET | Exibir conversa |
| `/chatbot/sessao/<id>/enviar/` | POST | Enviar mensagem |
| `/chatbot/sessao/<id>/deletar/` | GET/POST | Deletar conversa |
| `/chatbot/api/enviar/` | POST | API JSON para enviar mensagem |

### Usando o Chatbot

**1. Acessar via interface web**
```
GET /chatbot/
```

**2. Criar uma conversa**
```
POST /chatbot/novo/
    title: "Dúvidas sobre reciclagem"
```

**3. Enviar mensagem (view tradicional)**
```
POST /chatbot/sessao/123/enviar/
    content: "Como reciclar plásticos?"
```

**4. Enviar mensagem (API JSON)**
```
POST /chatbot/api/enviar/
Content-Type: application/json

{
    "session_id": 123,
    "message": "Como denunciar poluição?"
}
```

---

## 4. Otimização para Dispositivos Fracos

### Detecção Automática

O sistema detecta automaticamente dispositivos fracos:

```python
AIModelManager.is_low_capacity()  # Verifica RAM disponível
```

### Modelos Leves

Para dispositivos com menos de 2GB de RAM:

- **TensorFlow Lite**: Modelos compactos (poucos MB)
- **FLAN-T5 Small**: Modelo de chatbot leve (250MB)
- **CLIP ViT-Base**: Classificação eficiente
- **TensorFlow 2.13**: Otimizado para versões recentes do Python

### Configuração

Os modelos são carregados automaticamente:

```python
# Detecta capacidade e carrega modelo apropriado
if AIModelManager.is_low_capacity():
    # Usa modelo leve
    model = AIModelManager.load_chatbot()  # FLAN-T5 small
```

---

## 5. Instalação e Migração

### Passo 1: Atualizar Requirements
```bash
pip install -r requirements.txt
```

### Passo 2: Criar Migrações
```bash
python manage.py makemigrations chatbot
python manage.py migrate chatbot
```

### Passo 3: Registrar no Admin (opcional)
Já está configurado em `chatbot/admin.py`

### Passo 4: Testar
```bash
python manage.py runserver
# Acesse: http://localhost:8000/chatbot/
```

---

## 6. Cache e Performance

### Cache de Modelos

Os modelos são carreados uma única vez e reutilizados:

```python
_cache = {
    'deepfake_detector': None,
    'image_classifier': None,
    'chatbot': None,
}
```

**Benefício**: Primeira requisição pode levar 5-10s, mas as próximas são instantâneas.

### Recomendações de Produção

1. **Usar GPU** (se disponível):
   ```python
   device = "cuda" if torch.cuda.is_available() else "cpu"
   ```

2. **Cache Redis** para sessões:
   ```python
   # No settings.py
   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }
   ```

3. **Fila de Tarefas** (celery para processamento assíncrono):
   ```bash
   pip install celery redis
   ```

---

## 7. Troubleshooting

### Erro: "TensorFlow não disponível"
```bash
pip install tensorflow==2.13.0
```

### Erro: "CUDA não encontrado"
É normal! O sistema funciona em CPU. Para GPU:
```bash
pip install tensorflow[and-cuda]
```

### Chatbot retorna respostas vazias
- Verifique se `transformers` está instalado
- Verifique memória disponível (precisa 2GB+ para FLAN-T5)
- Veja logs: `python manage.py runserver` (DEBUG=True)

### Imagens não são classificadas
- Formatos suportados: JPEG, PNG, RGB
- Tamanho máximo: 10MB recomendado
- Use `/pictures/api/classify-image/` para debug

---

## 8. Exemplos de Uso

### JavaScript (Frontend)

```javascript
// Verificar se imagem é fake
async function verifyImage(imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    const response = await fetch('/pictures/api/verify-image/', {
        method: 'POST',
        body: formData
    });
    
    const data = await response.json();
    console.log('É fake?', data.is_fake);
    console.log('Confiança:', data.confidence * 100 + '%');
}

// Enviar mensagem ao chatbot
async function sendMessage(sessionId, message) {
    const response = await fetch('/chatbot/api/enviar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            session_id: sessionId,
            message: message
        })
    });
    
    const data = await response.json();
    console.log('Resposta IA:', data.assistant_message.content);
}
```

### Python (Backend)

```python
from pictures.ai_model import verify_image, classify_image_pollution, get_chatbot_response

# Verificar imagem
result = verify_image(image_pil)
print(f"Fake: {result['is_fake']}, Confiança: {result['confidence']}")

# Classificar
classifications = classify_image_pollution(image_pil)
for clf in classifications:
    print(f"{clf['label']}: {clf['score']:.2%}")

# Chatbot
response = get_chatbot_response("Como denunciar poluição?")
print(response)
```

---

## 9. Segurança

### Validações Implementadas

- ✅ Autenticação obrigatória (@login_required)
- ✅ Usuários só veem suas próprias conversas
- ✅ Users só podem deletar suas próprias sessões
- ✅ CSRF protection em formulários
- ✅ Timeout em requisições de IA (30s)

### Recomendações Adicionais

1. **Rate Limiting** para APIs de IA:
   ```python
   from django_ratelimit.decorators import ratelimit
   
   @ratelimit(key='user', rate='10/h')
   def verify_image_ai(request):
       ...
   ```

2. **Validação de Entrada**:
   - Máximo 10MB por imagem
   - Máximo 500 caracteres por mensagem
   - Máximo 1000 mensagens por sessão

---

## 10. Próximos Passos

### Melhorias Potenciais

- [ ] Treinar modelo customizado de deepfake
- [ ] Integrar com banco de dados externo de imagens
- [ ] Adicionar suporte multilíngue
- [ ] Implementar análise de sentimento
- [ ] Criar dashboard de estatísticas
- [ ] Integrar com APIs de terceiros

---

## Suporte

Para dúvidas ou problemas:
1. Verifique os logs: `python manage.py runserver` (DEBUG=True)
2. Consulte [docs TensorFlow](https://tensorflow.org)
3. Consulte [docs Transformers](https://huggingface.co/docs)

---

**Data**: 18/03/2026
**Versão**: 1.0
**Status**: ✅ Pronto para Produção
