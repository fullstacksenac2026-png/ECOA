# Projeto Integrador - Plataforma Educacional ECOA - Senac Sergipe

## Descrição do Projeto

Este é um projeto desenvolvido no curso de Programador Full Stack com o framework Django que implementa uma plataforma educacional completa, desenvolvida como trabalho integrador. A plataforma oferece funcionalidades para cursos, fórum de discussão, sistema de pagamentos, notificações, e integração com IA para análise de imagens.

## Funcionalidades Principais

### 1. Sistema de Autenticação e Autorização
- Cadastro e login de usuários
- Recuperação de senha
- Perfis de usuário com foto
- Controle de permissões

### 2. Módulo de Cursos
- Criação e gerenciamento de cursos
- Inscrição em cursos
- Conteúdo educacional

### 3. Fórum de Discussão
- Criação de tópicos
- Comentários e respostas
- Sistema de likes/votos
- Moderação de conteúdo

### 4. Sistema de Pagamentos
- Integração com Stripe e Mercado Pago
- Processamento de pagamentos
- Histórico de transações

### 5. Notificações
- Sistema de notificações em tempo real
- Alertas por email
- Notificações push

### 6. Análise de Imagens com IA Avançada
- **Detecção Multi-Método de Deepfakes**: 
  - Análise de frequência FFT para artefatos de compressão
  - Detecção facial usando MediaPipe
  - Análise de consistência de iluminação
  - Detecção de artefatos JPEG
  - Reconhecimento facial com OpenFace/MediaPipe fallback
  - Validação com datasets simulados (preparado para Kaggle)
- **Classificação Inteligente**: Transformers (CLIP) para categorização zero-shot
- **Chatbot**: FLAN-T5 para respostas contextuais
- **Otimização Mobile**: Detecção de dispositivos de baixa capacidade
- **Verificação de Autenticidade**: Sistema robusto para validar imagens enviadas

### 7. Relatórios
- Geração de relatórios administrativos
- Análise de dados da plataforma

## Tecnologias Utilizadas

- **Backend**: Django 4.2+
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **IA/ML**: 
  - Transformers 4.35+ (Hugging Face) - CLIP e FLAN-T5
  - PyTorch 2.1+ - Redes neurais
  - TensorFlow 2.13+ - Modelos de deep learning
  - OpenCV 4.8+ - Processamento de imagens
  - MediaPipe 0.10+ - Detecção facial e landmarks
  - NumPy 1.21+ - Computação numérica
  - PIL (Pillow) 10.0+ - Manipulação de imagens
  - Scikit-learn 1.3+ - Machine learning
  - Face Recognition (OpenFace) - Reconhecimento facial avançado
- **Pagamentos**: Stripe, Mercado Pago
- **Frontend**: HTML/CSS/JavaScript, Bootstrap 5.3+
- **Deploy**: Render, Heroku
- **Python**: 3.11+ (recomendado para deploy)

## Estrutura do Projeto

```
projeto_integrador/
├── authorization/     # Sistema de auth
├── chatbot/          # Módulo de chatbot
├── core/             # App principal
├── courses/          # Gestão de cursos
├── forum/            # Fórum de discussão
├── notifications/    # Sistema de notificações
├── payments/         # Processamento de pagamentos
├── pictures/         # Upload e análise de imagens
├── reports/          # Relatórios
└── projeto_integrador/  # Configurações principais
```

## Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- pip
- virtualenv

### Passos de Instalação

1. **Clone o repositório**
   ```bash
   git clone <url-do-repositorio>
   cd projeto_integrador
   ```

2. **Crie um ambiente virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o banco de dados**
   ```bash
   python manage.py migrate
   ```

5. **Crie um superusuário**
   ```bash
   python manage.py createsuperuser
   ```

6. **Execute o servidor**
   ```bash
   python manage.py runserver
   ```

## 🛠️ Painel Administrativo Avançado

A plataforma possui um dashboard administrativo premium com gráficos dinâmicos (estilo Recharts) acessível em:
`http://127.0.0.1:8000/admin/`

### Funcionalidades:
- **Gráficos Dinâmicos**: Distribuição de usuários (Ativos vs Bloqueados).
- **Métricas de Engajamento**: Gráficos de barras para imagens e denúncias.
- **Vanilla JS & ApexCharts**: Estética moderna com alta performance.

### Acesso Rápido (Superadmin):
- **CPF:** `97591432591`
- **Senha:** `admin123` (Ou a senha definida durante o `createsuperuser`)

## Funcionamento da IA

### Detecção de Imagens Manipuladas
O sistema utiliza **múltiplas técnicas avançadas** para detectar possíveis manipulações em imagens:

#### Técnicas Implementadas:
1. **Análise de Frequência FFT** (25% peso): Detecta artefatos de compressão JPEG
2. **Detecção Facial com MediaPipe** (30% peso): Analisa consistência de faces
3. **Análise de Iluminação** (25% peso): Verifica uniformidade de iluminação
4. **Artefatos de Compressão** (20% peso): Detecta padrões DCT

#### Processo:
1. **Pré-processamento**: Conversão para RGB e validação
2. **Análise Multi-Método**: Cada técnica retorna um score [0-1]
3. **Ponderação**: Scores combinados com pesos específicos
4. **Classificação**: Score final > 0.6 = potencialmente fake

#### Resposta Detalhada:
```json
{
    "is_fake": false,
    "confidence": 0.85,
    "message": "✅ Imagem parece AUTÊNTICA",
    "methods": [
        {"name": "FFT", "score": 0.4},
        {"name": "Face Detection", "score": 0.3},
        {"name": "Lighting", "score": 0.45}
    ]
}
```

### Classificação de Imagens
Usa o modelo CLIP (Contrastive Language-Image Pretraining) para classificação zero-shot de imagens em categorias relacionadas à poluição ambiental.

## Compatibilidade Mobile e Dispositivos

### Otimizações Implementadas
- **Detecção de Capacidade**: Sistema identifica dispositivos de baixa capacidade (< 2GB RAM)
- **Modelos Adaptativos**: IA usa modelos mais leves em dispositivos móveis
- **Templates Responsivos**: Interface otimizada para mobile com Bootstrap
- **Upload Dual-Mode**: Opção de câmera ou galeria para dispositivos móveis
- **Compressão Inteligente**: Imagens comprimidas automaticamente para mobile

### Funcionalidades Mobile
- **Captura de Imagem**: Interface nativa da câmera com fallback para upload
- **Análise em Tempo Real**: Processamento otimizado para dispositivos móveis
- **Interface Touch-Friendly**: Botões e navegação otimizados para toque
- **Offline Support**: Cache inteligente de modelos IA

### Navegadores Suportados
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Deploy

O projeto está configurado para deploy no Render/Heroku:

- **Procfile**: Define o comando de inicialização com Gunicorn
- **render.yaml**: Configuração para Render com MongoDB
- **runtime.txt**: Python 3.12.0
- **requirements.txt**: Dependências atualizadas para compatibilidade

### Configurações de Produção
- **DEBUG**: False
- **SECRET_KEY**: Definida via variável de ambiente
- **ALLOWED_HOSTS**: Configurado para domínios específicos
- **DATABASE_URL**: MongoDB Atlas para produção

### Deploy no Render
Para deploy bem-sucedido no Render, certifique-se de:
- Usar `python-3.11.9` no `runtime.txt`
- Manter versões conservadoras das dependências ML
- Configurar variáveis de ambiente corretamente
- Usar MongoDB Atlas como banco de dados

### Troubleshooting de Deploy

#### Erro: "No matching distribution found for tensorflow>=2.16.0"
**Solução**: Para ambientes de deploy, use versões mais conservadoras:
```txt
tensorflow>=2.13.0
tensorflow-hub>=0.13.0
runtime.txt: python-3.11.9
```

#### Erro: "RequestDataTooBig"
**Solução**: Aumentar limites de upload em `settings.py`:
```python
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB
```

#### Erro: "ModuleNotFoundError"
**Solução**: Verificar se todas as dependências estão listadas no requirements.txt com versões compatíveis com Python 3.12+.

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT.

## Contato

### Professor

- Sérgio Santana

### Alunos

- Leon Mendonça
- João Batista
- Max Gomes
- Guilherme Anthony
- Daniel Henrique
- Danilo Augusto
- Grazielle Feitosa


Para dúvidas ou sugestões, entre em contato com a equipe de desenvolvimento.