# Sistema de Cursos Estilo Coursera

## 📋 Visão Geral

Este é um sistema completo de gerenciamento de cursos online com estrutura semelhante à Coursera. Inclui:

- 📚 Estrutura de Seções e Lições
- 🎥 Player de Vídeos Integrado
- 💬 Sistema de Comentários com Replies
- 📝 Quiz com Múltiplos Tipos de Questões
- 📊 Rastreamento de Progresso
- ⭐ Sistema de Avaliações
- 🏆 Certificados ao Completar

---

## 🏗️ Estrutura de Modelos

### Modelos Principais

```
Course (Curso)
├── Section (Seção/Módulo)
│   └── Lesson (Lição)
│       ├── Video (Vídeo)
│       ├── Quiz (Quiz)
│       │   ├── QuizQuestion (Pergunta)
│       │   │   └── QuizAnswer (Resposta)
│       │   └── QuizResult (Resultado do Aluno)
│       └── Comment (Comentário)
├── Enrollment (Inscrição do Aluno)
├── Teacher (Professor)
└── UserLessonProgress (Progresso do Aluno)
```

---

## 🚀 Como Usar

### 1. Executar Migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Popular Dados de Exemplo

```bash
python manage.py seed_courses_new
```

### 3. Acessar Admin

```bash
python manage.py createsuperuser
python manage.py runserver
# Acesse: http://localhost:8000/admin
```

---

## 📖 URLs Disponíveis

### Urls de Cursos

| URL | Função |
|-----|--------|
| `/courses/courses/` | Lista todos os cursos |
| `/courses/courses/category/<id>/` | Cursos por categoria |
| `/courses/courses/<id>/` | Página inicial do curso |
| `/courses/courses/<id>/lessons/` | Dashboard de aulas |
| `/courses/lesson/<id>/video/` | Reprodutor de vídeo |
| `/courses/lesson/<id>/comments/add/` | Adicionar comentário |
| `/courses/comment/<id>/like/` | Like em comentário |
| `/courses/quiz/<id>/` | Fazer quiz |
| `/courses/quiz/<id>/results/` | Ver resultados |

---

## 🎯 Funcionalidades Principais

### 1. Página Inicial do Curso (`course-detail.html`)
- ✅ Descrição completa do curso
- ✅ Informações de professores
- ✅ Preview das seções e lições
- ✅ Seção de comentários
- ✅ Estatísticas (alunos, avaliação, duração)

### 2. Dashboard de Aulas (`course-lessons-detail.html`)
- ✅ Barra lateral com todas as seções
- ✅ Navegação entre lições
- ✅ Indicador de progresso
- ✅ Status de conclusão de lições

### 3. Reprodutor de Vídeo (`course-video.html`)
- ✅ Player de vídeo responsivo
- ✅ Transcrição do vídeo
- ✅ Sistema de comentários com replies
- ✅ Like em comentários
- ✅ Navegação entre vídeos
- ✅ Rastreamento automático de progresso

### 4. Quiz (`course-quiz.html`)
- ✅ Perguntas tipo múltipla escolha
- ✅ Perguntas verdadeiro/falso
- ✅ Perguntas de resposta curta
- ✅ Temporizador
- ✅ Navegador de questões
- ✅ Pontuação por pergunta

### 5. Resultados do Quiz (`course-quiz-results.html`)
- ✅ Score final em grande
- ✅ Percentual de acertos
- ✅ Detalhamento de cada questão
- ✅ Respostas corretas destacadas
- ✅ Histórico de tentativas
- ✅ Opção de tentar novamente
- ✅ Certificado ao passar

---

## 🔧 Customizações

### Adicionar uma Nova Lição

```python
from courses.models import Section, Lesson, Video

section = Section.objects.get(id=1)
lesson = Lesson.objects.create(
    section=section,
    title='Minha Lição',
    description='Descrição da lição',
    lesson_type='video',
    duration_minutes=30,
    order=3
)

Video.objects.create(
    lesson=lesson,
    video_url='https://www.youtube.com/embed/dQw4w9WgXcQ',
    transcript='Transcrição do vídeo...'
)
```

### Criar um Quiz

```python
from courses.models import Quiz, QuizQuestion, QuizAnswer

quiz = Quiz.objects.create(
    course=course,
    lesson=lesson,
    title='Quiz - Lição 1',
    passing_score=70,
    max_attempts=3
)

question = QuizQuestion.objects.create(
    quiz=quiz,
    text='Qual é a resposta?',
    question_type='multiple',
    points=1
)

QuizAnswer.objects.create(
    question=question,
    text='Resposta Correta',
    is_correct=True
)

QuizAnswer.objects.create(
    question=question,
    text='Resposta Errada',
    is_correct=False
)
```

---

## 📊 Campos de Modelos

### Course
- `name`: Nome do curso
- `description`: Descrição detalhada
- `price`: Preço do curso
- `time`: Duração total (ex: "40 horas")
- `image`: Imagem de capa
- `rating`: Avaliação (0-5)
- `students_count`: Número de alunos
- `created_at`, `updated_at`: Datas

### Section
- `course`: Foreign Key para Course
- `title`: Nome da seção
- `description`: Descrição
- `order`: Ordem de exibição

### Lesson
- `section`: Foreign Key para Section
- `title`: Nome da lição
- `description`: Descrição
- `lesson_type`: Tipo (video, text, assignment)
- `duration_minutes`: Duração
- `order`: Ordem

### Video
- `lesson`: One-to-One com Lesson
- `video_url`: URL do vídeo (YouTube, Vimeo, etc)
- `transcript`: Transcrição em texto

### Quiz
- `course`: Foreign Key para Course
- `lesson`: Foreign Key para Lesson (opcional)
- `title`: Nome do quiz
- `description`: Descrição
- `passing_score`: Nota mínima para passar (0-100)
- `max_attempts`: Número máximo de tentativas

### QuizQuestion
- `quiz`: Foreign Key para Quiz
- `text`: Texto da pergunta
- `question_type`: Tipo (multiple, true_false, short_answer)
- `order`: Ordem
- `points`: Pontos da questão

### QuizAnswer
- `question`: Foreign Key para QuizQuestion
- `text`: Texto da resposta
- `is_correct`: Se é a resposta correta
- `order`: Ordem

### Comment
- `lesson`: Foreign Key para Lesson
- `course`: Foreign Key para Course
- `user`: Foreign Key para User
- `content`: Texto do comentário
- `parent_comment`: Foreign Key para Comment (para replies)
- `likes_count`: Número de likes

### UserLessonProgress
- `lesson`: Foreign Key para Lesson
- `user`: Foreign Key para User
- `is_completed`: Se foi completado
- `progress_percentage`: Percentual de progresso
- `started_at`, `completed_at`: Datas

---

## 🎨 Customização de Templates

Todos os templates usam Bootstrap 5 e estão em `courses/templates/`:

- `course-detail.html` - Página inicial
- `course-lessons-detail.html` - Dashboard
- `course-video.html` - Player de vídeo
- `course-quiz.html` - Interface de quiz
- `course-quiz-results.html` - Resultados

---

## 🔐 Permissões e Autenticação

Todas as páginas de aprendizado requerem:
1. Usuário autenticado (`@login_required`)
2. Matrícula no curso (`Enrollment` verificado)

---

## 📱 Responsividade

Todos os componentes são totalmente responsivos:
- ✅ Desktop
- ✅ Tablet
- ✅ Mobile

---

## 🐛 Troubleshooting

### Erro ao acessar Quiz
- Verifique se o Quiz tem perguntas
- Confirme se o usuário está matriculado

### Vídeo não aparece
- Confirme a URL do vídeo
- Use YouTube Embed URLs: `https://www.youtube.com/embed/VIDEO_ID`

### Comentários não salvam
- Verifique permissões CSRF
- Confirme se o usuário está autenticado

---

## 📚 Próximos Passos

- [ ] Adicionar certificados PDF
- [ ] Implementar live classes
- [ ] Adicionar gamificação (badges, points)
- [ ] Sistema de notificações
- [ ] API REST
- [ ] Análise de progresso do aluno

---

## 📝 Licença

Este projeto é parte do Projeto Integrador Senac.

---

## 👨‍💻 Desenvolvido por

Seu Nome / Equipe

**Última atualização:** Fevereiro 2026
