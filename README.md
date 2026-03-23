# Projeto Integrador - Plataforma Educacional

## Descrição do Projeto

Este é um projeto Django que implementa uma plataforma educacional completa, desenvolvida como trabalho integrador. A plataforma oferece funcionalidades para cursos, fórum de discussão, sistema de pagamentos, notificações, e integração com IA para análise de imagens.

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

### 6. Análise de Imagens com IA
- Detecção de imagens manipuladas/fake usando análise de frequência FFT
- Classificação de imagens usando Transformers (CLIP)
- Verificação de autenticidade de imagens enviadas

### 7. Relatórios
- Geração de relatórios administrativos
- Análise de dados da plataforma

## Tecnologias Utilizadas

- **Backend**: Django 4.x
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **IA/ML**: 
  - Transformers 3.12.0 (Hugging Face)
  - PyTorch 2.0.1
  - OpenCV
  - NumPy
  - PIL (Pillow)
- **Pagamentos**: Stripe, Mercado Pago
- **Frontend**: HTML/CSS/JavaScript, Bootstrap
- **Deploy**: Render, Heroku

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

## Funcionamento da IA

### Detecção de Imagens Manipuladas
O sistema utiliza análise de frequência FFT para detectar possíveis manipulações em imagens:

1. **Conversão**: Imagem convertida para escala de cinza
2. **FFT**: Aplicada Transformada de Fourier
3. **Análise**: Comparação entre frequências baixas e altas
4. **Classificação**: Baseada em limiares estatísticos

### Classificação de Imagens
Usa o modelo CLIP (Contrastive Language-Image Pretraining) para classificação zero-shot de imagens em categorias pré-definidas.

## Deploy

O projeto está configurado para deploy no Render/Heroku:

- **Procfile**: Define o comando de inicialização
- **render.yaml**: Configuração para Render
- **runtime.txt**: Versão do Python
- **build.sh**: Script de build

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT.

## Contato

Para dúvidas ou sugestões, entre em contato com a equipe de desenvolvimento.