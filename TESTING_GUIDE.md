# Guia de Teste - Sistema de Cursos

## 🚀 Iniciando o Ambiente

### 1. Criar Superusuário
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: admin123
```

### 2. Executar Migrações
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Seed de Dados
```bash
python manage.py seed_courses_new
```

### 4. Criar Usuário Teste (Aluno)
```bash
python manage.py shell

from authorization.models import User
from courses.models import Course, Enrollment

# Criar usuário
user = User.objects.create_user(
    username='aluno',
    email='aluno@example.com',
    password='aluno123'
)

# Matricular no curso
course = Course.objects.first()
Enrollment.objects.create(user=user, course=course)

print('✓ Usuário criado e matriculado com sucesso!')
exit()
```

---

## 🧪 Cenários de Teste

### Teste 1: Página Inicial do Curso
1. Acesse `/courses/courses/` 
2. Clique em um curso
3. Verifique:
   - ✅ Descrição aparece
   - ✅ Seções estão listadas
   - ✅ Comentários aparecem
   - ✅ Informações de professores aparecem

### Teste 2: Dashboard de Aulas
1. Faça login como `aluno` / `aluno123`
2. Acesse um curso
3. Clique em "Ir para Aulas"
4. Verifique:
   - ✅ Barra lateral mostra todas as seções
   - ✅ Progresso está em 0%
   - ✅ Todas as lições estão listadas

### Teste 3: Vídeo e Comentários
1. Clique em uma lição de vídeo
2. Verifique:
   - ✅ Vídeo aparece
   - ✅ Transcrição aparece
   - ✅ Pode adicionar comentário
   - ✅ Pode dar like em comentário
   - ✅ Progresso vai para 100%

### Teste 4: Quiz
1. Encontre um quiz no final de uma seção
2. Clique em fazer quiz
3. Verifique:
   - ✅ Todas as questões aparecem
   - ✅ Temporizador funciona
   - ✅ Pode selecionar respostas
   - ✅ Status de questões muda

### Teste 5: Resultados de Quiz
1. Após responder o quiz
2. Verifique:
   - ✅ Score aparece grande
   - ✅ Percentual está correto
   - ✅ Respostas corretas aparecem destacadas
   - ✅ Pode tentar novamente (se permitido)

### Teste 6: Histórico de Quiz
1. Faça o quiz várias vezes
2. Acesse resultados
3. Verifique:
   - ✅ Histórico mostra todas as tentativas
   - ✅ Status (Aprovado/Reprovado) aparece
   - ✅ Pode ver resultado de cada tentativa

---

## 📊 Casos de Teste Detalhados

### CT-01: Criar Curso
```
Objetivo: Verificar criação de novo curso
Pré-requisito: Estar no admin
Passos:
1. Vá para /admin/courses/course/
2. Clique em "Adicionar Curso"
3. Preencha os dados:
   - Nome: "Django Avançado"
   - Descrição: "Aprenda Django em nível avançado"
   - Preço: 149.90
   - Tempo: 60 horas
4. Clique em "Salvar"
Resultado Esperado: Curso criado com sucesso
```

### CT-02: Criar Seção com Lições
```
Objetivo: Criar estrutura completa de aula
Pré-requisito: Ter um curso
Passos:
1. Vá para /admin/courses/section/
2. Clique em "Adicionar Seção"
3. Preencha:
   - Curso: Selecione o curso
   - Título: "Módulo 1: Fundamentos"
   - Ordem: 0
4. Salve
5. Crie 3 lições nessa seção
6. Para cada lição, adicione um vídeo
Resultado Esperado: Sistema permite navegação completa
```

### CT-03: Criar Quiz com Questões
```
Objetivo: Criar quiz funcional
Pré-requisito: Ter lições
Passos:
1. Vá para /admin/courses/quiz/
2. Clique em "Adicionar Quiz"
3. Configure:
   - Curso: Selecione
   - Lição: Selecione
   - Título: "Teste Módulo 1"
   - Passing Score: 70
   - Max Attempts: 3
4. Adicione questões usando o inline
5. Para cada questão, adicione respostas
6. Marque 1 resposta como correta
Resultado Esperado: Quiz salvo com sucesso
```

### CT-04: Fazer Quiz como Aluno
```
Objetivo: Fazer um quiz completo
Pré-requisito: Estar matriculado e quizzes existirem
Passos:
1. Acesse o curso
2. Vá para aulas
3. Navegue até a quizz
4. Responda todas as questões
5. Clique em "Enviar Respostas"
6. Veja os resultados
Resultado Esperado: 
- Respostas são salvas
- Resultado mostra corretas/incorretas
- Mensagem de sucesso/falha aparece
```

---

## 🐛 Testes de Bug

### Bug-01: Progresso não atualiza
```
Passos: Repita teste 3
Reprodução do Bug:
- Se progresso não vai para 100% após assistir vídeo
- Se sidebar não atualiza
Solução: Verificar middleware de progresso
```

### Bug-02: Quiz não salva respostas
```
Passos: Repita teste 4
Reprodução do Bug:
- Se clicar em resposta e não marcar
- Se recarregar página e resposta fica
Solução: Verificar validação form Django
```

### Bug-03: Comentário duplicado
```
Passos: 
- Comentar em um vídeo
- Recarregar página
Reprodução do Bug:
- Se comentário aparece duplicado
Solução: Verificar ID do comentário no form
```

---

## ✅ Checklist Final

- [ ] Todos os modelos foram criados
- [ ] Admin está funcional
- [ ] URLs estão configuradas
- [ ] Templates aparecem sem erros
- [ ] Autenticação funciona
- [ ] Matrículas funcionam
- [ ] Comentários salvam e aparecem
- [ ] Quiz salva respostas
- [ ] Resultados calculam corretamente
- [ ] Progresso atualiza
- [ ] Mobile é responsivo

---

## 📞 Contato

Em caso de dúvidas, verifique:
1. COURSES_README.md
2. Django console: `python manage.py shell`
3. Logs: `tail -f logs/django.log`

---

**Versão:** 1.0  
**Data:** Fevereiro 2026
