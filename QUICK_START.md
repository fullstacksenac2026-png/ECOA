# 🚀 Guia Rápido de Uso - IA no Projeto

## ✨ O que foi implementado?

1. **Detecção de Deepfake** - Verifica se uma imagem é real ou fake
2. **Classificação de Imagens** - Categoriza imagens de poluição
3. **Chatbot** - Assistente de IA para responder dúvidas
4. **APIs** - Endpoints para integração

---

## 📦 Instalação (5 minutos)

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

⏱️ **Tempo**: ~5 minutos (primeirão carrega modelos)

### 2. Criar Banco de Dados
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Testar
```bash
python manage.py runserver
```

Acesse: `http://localhost:8000/chatbot/`

---

## 🎮 Como Usar

### A. Tirar Foto com IA

1. Vá para **Pictures → Take Picture**
2. Tire uma foto
3. A IA vai:
   - ✅ Verificar se é real ou fake
   - ✅ Classificar a poluição
   - ✅ Sugerir localização
4. Complete a denúncia

### B. Usar o Chatbot

1. Vá para `/chatbot/`
2. Clique em **"Nova Conversa"**
3. Escolha um título
4. Digite sua pergunta
5. O assistente responde!

**Exemplos de perguntas**:
- "Como faço uma denúncia de poluição?"
- "Quais são os tipos de poluição?"
- "Como reciclar corretamente?"

### C. Usar API de Deepfake

```javascript
// Verificar se imagem é fake
const formData = new FormData();
formData.append('image', imageFile);

const response = await fetch('/pictures/api/verify-image/', {
    method: 'POST',
    body: formData
});

const data = await response.json();
console.log(data.is_fake);      // true/false
console.log(data.confidence);   // 0-1
```

### D. Usar API de Classificação

```javascript
// Classificar imagem
const formData = new FormData();
formData.append('image', imageFile);

const response = await fetch('/pictures/api/classify-image/', {
    method: 'POST',
    body: formData
});

const data = await response.json();
data.classifications.forEach(c => {
    console.log(c.label, c.score);
});
```

---

## 🔑 URLs Importantes

| Funcionalidade | URL |
|---|---|
| Chatbot - Listar | `/chatbot/` |
| Chatbot - Novo | `/chatbot/novo/` |
| Chatbot - Conversa | `/chatbot/sessao/<id>/` |
| API Deepfake | `POST /pictures/api/verify-image/` |
| API Classificação | `POST /pictures/api/classify-image/` |
| Admin Chatbot | `/admin/chatbot/` |

---

## 🆘 Problemas Comuns

### "TensorFlow não encontrado"
```bash
pip install tensorflow==2.13.0
```

### "Modelo não carrega"
- Primeira execução leva 5-10 segundos
- Próximas são instantâneas
- Verifique conexão de internet

### "Chatbot não responde"
- Verifique: `pip install transformers`
- Verifique RAM disponível (precisa 2GB+)
- Veja logs do servidor (DEBUG=True)

---

## 📊 Respaldo de Dados

As conversas são salvas no banco:

```python
# Ver todas as conversas
ChatSession.objects.all()

# Ver mensagens de uma conversa
session = ChatSession.objects.get(id=1)
session.messages.all()
```

---

## ⚙️ Configurações Importantes

### Modo Leve (Dispositivos Fracos)
Automático! O sistema detecta:
- Dispositivos móveis
- Conexões lentas
- Pouca RAM

### Cache de Modelos
Os modelos são carregados **uma única vez** e reutilizados. Primeira requisição leva mais tempo.

---

## 🎓 Exemplo: Chat Full

```
Usuário: "Qual é o primeiro passo para denunciar poluição?"

IA: "O primeiro passo é coletar evidências! Você pode:
1. Tirar fotos ou vídeos do problema
2. Anotar data, hora e local
3. Usar nosso app para fazer a denúncia
4. Incluir descrição detalhada
5. Anexar comprovante geográfico

Você tem fotos? Posso ajudar a analisá-las!"

Usuário: "Como saber se minha foto é real?"

IA: "Só uma curiosidade ou você suspeita que a foto é manipulada?
Se for o caso, você pode:
1. Usar nosso verificador de deepfake
2. Procurar artefatos digitais
3. Comparar com a cena real
4. Consultar especialistas

Diga se precisa de ajuda!"
```

---

## 📈 Monitor de Uso

Veja quantas conversas cada usuário teve:
```python
from chatbot.models import ChatSession
from django.db.models import Count

# Usuários mais ativos
ChatSession.objects.values('user__email').annotate(
    total=Count('id')
).order_by('-total')[:10]
```

---

## 🔐 Segurança

Tudo é protegido:
- ✅ Apenas usuários autenticados
- ✅ Cada um vê apenas seus dados
- ✅ Proteção CSRF ativada
- ✅ Validação de entrada

---

## 📞 Próximas Etapas

Depois que tiver funcionando, considere:

1. **Treinar modelo customizado** de deepfake
2. **Adicionar estatísticas** de uso
3. **Exportar conversas** em PDF
4. **Integrar com WhatsApp** para chatbot
5. **Adicionar análise de sentimento**

---

## 💡 Dicas de Produção

```bash
# Coleta de estáticos
python manage.py collectstatic --noinput

# Backup de dados
python manage.py dumpdata chatbot > chatbot_backup.json

# Logs
# Configure em settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'ai.log',
        },
    },
    'loggers': {
        'pictures.ai_model': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

---

## 🎉 Pronto para Usar!

Seu projeto agora tem:
- ✅ Detecção de deepfake
- ✅ Classificação automática
- ✅ Chatbot 24/7
- ✅ APIs prontas
- ✅ Interface web completa

**Próximo passo**: Acessar `/chatbot/` e testar!

---

**Versão**: 1.0  
**Data**: 18/03/2026  
**Status**: ✅ PRONTO
