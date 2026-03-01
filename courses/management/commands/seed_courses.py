from django.core.management.base import BaseCommand
from courses.models import (
    Course, VideoCourse, CourseMaterial, Quiz, QuizQuestion, QuizAnswer,
    TextContentCoursePage, Category
)


class Command(BaseCommand):
    help = 'Seeds the database with 10 complete courses with videos, materials, and quizzes'

    def handle(self, *args, **options):
        # Clear existing data
        Course.objects.all().delete()
        Category.objects.all().delete()

        courses_data = [
            {
                'name': 'Python para Iniciantes',
                'description': 'Aprenda os fundamentos da linguagem Python, desde o básico até conceitos intermediários. Perfeito para quem quer começar na programação.',
                'price': '99.90',
                'time': '40 horas',
                'videos': [
                    {'title': 'Introdução ao Python', 'url': 'https://www.youtube.com/embed/S9uPNwFXMs8', 'time': '45 min'},
                    {'title': 'Variáveis e Tipos de Dados', 'url': 'https://www.youtube.com/embed/KVE8ufRvMR8', 'time': '1h 15min'},
                    {'title': 'Estruturas de Controle', 'url': 'https://www.youtube.com/embed/5f90kP4tHgA', 'time': '1h 30min'},
                ],
                'materials': [
                    {'title': 'Guia Completo Python.pdf', 'url': 'https://example.com/python-guide.pdf'},
                    {'title': 'Exemplos de Código', 'url': 'https://example.com/python-examples.zip'},
                    {'title': 'Cheat Sheet Python', 'url': 'https://example.com/cheat-sheet.pdf'},
                ],
                'quizzes': [
                    {
                        'title': 'Quiz - Fundamentos',
                        'questions': [
                            {'text': 'Qual é a palavra-chave para criar uma função em Python?',
                             'answers': [
                                 {'text': 'def', 'is_correct': True},
                                 {'text': 'function', 'is_correct': False},
                                 {'text': 'func', 'is_correct': False},
                                 {'text': 'define', 'is_correct': False},
                             ]},
                            {'text': 'Como se cria uma lista em Python?',
                             'answers': [
                                 {'text': '[1, 2, 3]', 'is_correct': True},
                                 {'text': '{1, 2, 3}', 'is_correct': False},
                                 {'text': '(1, 2, 3)', 'is_correct': False},
                                 {'text': '<1, 2, 3>', 'is_correct': False},
                             ]},
                            {'text': 'Qual é o tipo de dado para 3.14?',
                             'answers': [
                                 {'text': 'float', 'is_correct': True},
                                 {'text': 'int', 'is_correct': False},
                                 {'text': 'string', 'is_correct': False},
                                 {'text': 'number', 'is_correct': False},
                             ]},
                            {'text': 'Como você comenta uma linha em Python?',
                             'answers': [
                                 {'text': '# comentário', 'is_correct': True},
                                 {'text': '// comentário', 'is_correct': False},
                                 {'text': '/* comentário */', 'is_correct': False},
                                 {'text': '-- comentário', 'is_correct': False},
                             ]},
                        ]
                    },
                ]
            },
            {
                'name': 'Django Web Framework',
                'description': 'Domine o Django, o framework web mais popular do Python. Crie aplicações robustas e escaláveis com este curso completo.',
                'price': '149.90',
                'time': '50 horas',
                'videos': [
                    {'title': 'Setup do Django', 'url': 'https://www.youtube.com/embed/jBzwzrDvZ18', 'time': '30 min'},
                    {'title': 'Models e Banco de Dados', 'url': 'https://www.youtube.com/embed/0oxyiJ2jYV0', 'time': '2h'},
                    {'title': 'Views e URLs', 'url': 'https://www.youtube.com/embed/rHux0gMZ3Eg', 'time': '1h 45min'},
                ],
                'materials': [
                    {'title': 'Documentação Django Oficial', 'url': 'https://example.com/django-docs.pdf'},
                    {'title': 'Projeto Exemplo Completo', 'url': 'https://example.com/django-project.zip'},
                ],
                'quizzes': [
                    {
                        'title': 'Quiz - Django Basics',
                        'questions': [
                            {'text': 'Qual comando inicia um novo projeto Django?',
                             'answers': [
                                 {'text': 'django-admin startproject', 'is_correct': True},
                                 {'text': 'python manage.py new', 'is_correct': False},
                                 {'text': 'django new', 'is_correct': False},
                                 {'text': 'pip install django', 'is_correct': False},
                             ]},
                            {'text': 'O que é um app no Django?',
                             'answers': [
                                 {'text': 'Um módulo contendo models, views e templates', 'is_correct': True},
                                 {'text': 'Um arquivo Python', 'is_correct': False},
                                 {'text': 'Um banco de dados', 'is_correct': False},
                                 {'text': 'Uma pasta de configuração', 'is_correct': False},
                             ]},
                            {'text': 'Qual é o ORM do Django?',
                             'answers': [
                                 {'text': 'Models', 'is_correct': True},
                                 {'text': 'Views', 'is_correct': False},
                                 {'text': 'Templates', 'is_correct': False},
                                 {'text': 'Migrations', 'is_correct': False},
                             ]},
                            {'text': 'Como executar migrações no Django?',
                             'answers': [
                                 {'text': 'python manage.py migrate', 'is_correct': True},
                                 {'text': 'django migrate', 'is_correct': False},
                                 {'text': 'python migrate.py', 'is_correct': False},
                                 {'text': 'manage.py run migrate', 'is_correct': False},
                             ]},
                        ]
                    },
                ]
            },
            {
                'name': 'JavaScript Avançado',
                'description': 'Domine JavaScript moderno com ES6+, async/await, promises e muito mais. Torne-se um desenvolvedor JavaScript profissional.',
                'price': '119.90',
                'time': '45 horas',
                'videos': [
                    {'title': 'ES6 e Sintaxe Moderna', 'url': 'https://www.youtube.com/embed/PkZNo7MFNFg', 'time': '2h'},
                    {'title': 'Async/Await e Promises', 'url': 'https://www.youtube.com/embed/exBgWAu54qA', 'time': '1h 30min'},
                    {'title': 'DOM Manipulation', 'url': 'https://www.youtube.com/embed/5fb2aJ1mUEU', 'time': '1h 45min'},
                ],
                'materials': [
                    {'title': 'JavaScript Handbook.pdf', 'url': 'https://example.com/js-handbook.pdf'},
                    {'title': 'Código Fonte dos Exemplos', 'url': 'https://example.com/js-examples.zip'},
                    {'title': 'Referência Rápida ES6', 'url': 'https://example.com/es6-reference.pdf'},
                ],
                'quizzes': [
                    {
                        'title': 'Quiz - JavaScript Moderno',
                        'questions': [
                            {'text': 'Qual é a diferença entre let e var?',
                             'answers': [
                                 {'text': 'let tem escopo de bloco, var tem escopo de função', 'is_correct': True},
                                 {'text': 'Não há diferença', 'is_correct': False},
                                 {'text': 'var é melhor que let', 'is_correct': False},
                                 {'text': 'let só funciona em navegadores', 'is_correct': False},
                             ]},
                            {'text': 'O que é uma Promise?',
                             'answers': [
                                 {'text': 'Um objeto que representa o resultado eventual de uma operação assíncrona', 'is_correct': True},
                                 {'text': 'Uma função de callback', 'is_correct': False},
                                 {'text': 'Um tipo de loop', 'is_correct': False},
                                 {'text': 'Uma string', 'is_correct': False},
                             ]},
                            {'text': 'Como usar async/await?',
                             'answers': [
                                 {'text': 'async define função assíncrona, await espera by Promise', 'is_correct': True},
                                 {'text': 'São sinônimos', 'is_correct': False},
                                 {'text': 'Usados em HTML', 'is_correct': False},
                                 {'text': 'Apenas em servidores', 'is_correct': False},
                             ]},
                            {'text': 'O que é arrow function?',
                             'answers': [
                                 {'text': 'Sintaxe de função com =>', 'is_correct': True},
                                 {'text': 'Uma função que aponta para algo', 'is_correct': False},
                                 {'text': 'Uma classe JavaScript', 'is_correct': False},
                                 {'text': 'Um tipo de array', 'is_correct': False},
                             ]},
                        ]
                    },
                ]
            },
            {
                'name': 'React.js Completo',
                'description': 'Aprenda React do zero. Componentes, hooks, estado, context API e integração com API REST. Crie aplicações modernas.',
                'price': '139.90',
                'time': '55 horas',
                'videos': [
                    {'title': 'Fundamentos do React', 'url': 'https://www.youtube.com/embed/dQw4w9WgXcQ', 'time': '2h 30min'},
                    {'title': 'Hooks e Gerenciamento de Estado', 'url': 'https://www.youtube.com/embed/dpw9EHDh2bM', 'time': '2h'},
                    {'title': 'Consumindo APIs com React', 'url': 'https://www.youtube.com/embed/cF1qbepASVc', 'time': '1h 45min'},
                ],
                'materials': [
                    {'title': 'Guia Completo React.pdf', 'url': 'https://example.com/react-guide.pdf'},
                    {'title': 'Projeto React Todo App', 'url': 'https://example.com/react-todo.zip'},
                    {'title': 'Hooks Cheat Sheet', 'url': 'https://example.com/hooks-cheat.pdf'},
                ],
                'quizzes': [
                    {
                        'title': 'Quiz - React Essentials',
                        'questions': [
                            {'text': 'O que é um componente React?',
                             'answers': [
                                 {'text': 'Uma função ou classe que retorna JSX', 'is_correct': True},
                                 {'text': 'Um arquivo CSS', 'is_correct': False},
                                 {'text': 'Uma API', 'is_correct': False},
                                 {'text': 'Um banco de dados', 'is_correct': False},
                             ]},
                            {'text': 'Qual hook atualiza o estado em React?',
                             'answers': [
                                 {'text': 'useState', 'is_correct': True},
                                 {'text': 'useAPI', 'is_correct': False},
                                 {'text': 'useEffect', 'is_correct': False},
                                 {'text': 'useData', 'is_correct': False},
                             ]},
                            {'text': 'O que é JSX?',
                             'answers': [
                                 {'text': 'Sintaxe que permite escrever HTML em JavaScript', 'is_correct': True},
                                 {'text': 'Uma linguagem separada', 'is_correct': False},
                                 {'text': 'Um tipo de CSS', 'is_correct': False},
                                 {'text': 'Uma biblioteca', 'is_correct': False},
                             ]},
                            {'text': 'O que useEffect faz?',
                             'answers': [
                                 {'text': 'Executa efeitos colaterais em componentes funcionais', 'is_correct': True},
                                 {'text': 'Define propriedades', 'is_correct': False},
                                 {'text': 'Cria loops', 'is_correct': False},
                                 {'text': 'Estiliza componentes', 'is_correct': False},
                             ]},
                        ]
                    },
                ]
            },
            {
                'name': 'SQL e Banco de Dados',
                'description': 'Domine SQL, design de banco de dados relacionais e otimização. Essencial para todo desenvolvedor backend.',
                'price': '99.90',
                'time': '35 horas',
                'videos': [
                    {'title': 'Introdução a SQL', 'url': 'https://www.youtube.com/embed/BL8ibS2fpXE', 'time': '1h 30min'},
                    {'title': 'JOINs e Relacionamentos', 'url': 'https://www.youtube.com/embed/0OTZiV2KYOE', 'time': '2h'},
                    {'title': 'Otimização e Índices', 'url': 'https://www.youtube.com/embed/mIJRzn-Bkxw', 'time': '1h 45min'},
                ],
                'materials': [
                    {'title': 'SQL Reference Guide.pdf', 'url': 'https://example.com/sql-guide.pdf'},
                    {'title': 'Scripts SQL Úteis', 'url': 'https://example.com/sql-scripts.zip'},
                    {'title': 'Diagramas ER', 'url': 'https://example.com/er-diagrams.pdf'},
                ],
                'quizzes': [
                    {
                        'title': 'Quiz - SQL Fundamentals',
                        'questions': [
                            {'text': 'Qual comando seleciona dados?',
                             'answers': [
                                 {'text': 'SELECT', 'is_correct': True},
                                 {'text': 'GET', 'is_correct': False},
                                 {'text': 'FETCH', 'is_correct': False},
                                 {'text': 'RETRIEVE', 'is_correct': False},
                             ]},
                            {'text': 'O que é PRIMARY KEY?',
                             'answers': [
                                 {'text': 'Identificador único de um registro', 'is_correct': True},
                                 {'text': 'Uma senha', 'is_correct': False},
                                 {'text': 'Uma coluna importante', 'is_correct': False},
                                 {'text': 'Um tipo de índice', 'is_correct': False},
                             ]},
                            {'text': 'Como fazer INNER JOIN?',
                             'answers': [
                                 {'text': 'SELECT * FROM tabela1 JOIN tabela2 ON condição', 'is_correct': True},
                                 {'text': 'SELECT * FROM tabela1, tabela2', 'is_correct': False},
                                 {'text': 'SELECT * MERGE tabela1 tabela2', 'is_correct': False},
                                 {'text': 'SELECT join(tabela1, tabela2)', 'is_correct': False},
                             ]},
                            {'text': 'O que é uma FOREIGN KEY?',
                             'answers': [
                                 {'text': 'Referência para chave primária de outra tabela', 'is_correct': True},
                                 {'text': 'Uma chave secundária', 'is_correct': False},
                                 {'text': 'Uma cópia da chave primária', 'is_correct': False},
                                 {'text': 'Um tipo de índice', 'is_correct': False},
                             ]},
                        ]
                    },
                ]
            },
            {
                'name': 'Git e Controle de Versão',
                'description': 'Aprenda Git profundamente. Branching, merging, rebase e colaboração em equipe. Essencial para todo desenvolvedor.',
                'price': '79.90',
                'time': '20 horas',
                'videos': [
                    {'title': 'Iniciando com Git', 'url': 'https://www.youtube.com/embed/USjZcfj8yxE', 'time': '1h'},
                    {'title': 'Branches e Merging', 'url': 'https://www.youtube.com/embed/QV0kVNvkMxc', 'time': '1h 30min'},
                    {'title': 'Colaboração com GitHub', 'url': 'https://www.youtube.com/embed/w3jLJU7DT5E', 'time': '1h 15min'},
                ],
                'materials': [
                    {'title': 'Git Workflow Guide.pdf', 'url': 'https://example.com/git-guide.pdf'},
                    {'title': 'Git Commands Cheat Sheet', 'url': 'https://example.com/git-cheat.pdf'},
                ],
                'quizzes': [
                    {
                        'title': 'Quiz - Git Basics',
                        'questions': [
                            {'text': 'Qual comando inicia um repositório Git?',
                             'answers': [
                                 {'text': 'git init', 'is_correct': True},
                                 {'text': 'git create', 'is_correct': False},
                                 {'text': 'git start', 'is_correct': False},
                                 {'text': 'git new', 'is_correct': False},
                             ]},
                            {'text': 'Como criar uma nova branch?',
                             'answers': [
                                 {'text': 'git checkout -b nome-branch', 'is_correct': True},
                                 {'text': 'git new branch', 'is_correct': False},
                                 {'text': 'git create-branch', 'is_correct': False},
                                 {'text': 'git add branch', 'is_correct': False},
                             ]},
                            {'text': 'O que faz git add?',
                             'answers': [
                                 {'text': 'Coloca arquivos na staging area', 'is_correct': True},
                                 {'text': 'Cria novo arquivo', 'is_correct': False},
                                 {'text': 'Deleta arquivo', 'is_correct': False},
                                 {'text': 'Envia para servidor', 'is_correct': False},
                             ]},
                            {'text': 'Como visualizar histórico?',
                             'answers': [
                                 {'text': 'git log', 'is_correct': True},
                                 {'text': 'git history', 'is_correct': False},
                                 {'text': 'git show', 'is_correct': False},
                                 {'text': 'git status', 'is_correct': False},
                             ]},
                        ]
                    },
                ]
            },
            {
                'name': 'CSS Avançado e Responsivo',
                'description': 'Domine CSS moderno, Flexbox, Grid, animações e design responsivo. Crie interfaces bonitas e funcionais.',
                'price': '89.90',
                'time': '32 horas',
                'videos': [
                    {'title': 'Fundamentos de CSS', 'url': 'https://www.youtube.com/embed/wXxVHkjPnHU', 'time': '1h 45min'},
                    {'title': 'Flexbox e Grid Layout', 'url': 'https://www.youtube.com/embed/hs3piaN4b5I', 'time': '2h 15min'},
                    {'title': 'Animações e Transições', 'url': 'https://www.youtube.com/embed/YszONiN3Eto', 'time': '1h 30min'},
                ],
                'materials': [
                    {'title': 'CSS Modern Handbook.pdf', 'url': 'https://example.com/css-handbook.pdf'},
                    {'title': 'Projetos Exemplo CSS', 'url': 'https://example.com/css-projects.zip'},
                    {'title': 'Animation Library', 'url': 'https://example.com/animations.css'},
                ],
                'quizzes': [
                    {
                        'title': 'Quiz - CSS Skills',
                        'questions': [
                            {'text': 'Qual propriedade cria layout flexível?',
                             'answers': [
                                 {'text': 'display: flex', 'is_correct': True},
                                 {'text': 'display: flexible', 'is_correct': False},
                                 {'text': 'layout: flex', 'is_correct': False},
                                 {'text': 'flex: true', 'is_correct': False},
                             ]},
                            {'text': 'Como centralizar com Flexbox?',
                             'answers': [
                                 {'text': 'justify-content: center; align-items: center', 'is_correct': True},
                                 {'text': 'text-align: center', 'is_correct': False},
                                 {'text': 'center: true', 'is_correct': False},
                                 {'text': 'align: center', 'is_correct': False},
                             ]},
                            {'text': 'O que cria layouts em duas dimensões?',
                             'answers': [
                                 {'text': 'CSS Grid', 'is_correct': True},
                                 {'text': 'CSS Flexbox', 'is_correct': False},
                                 {'text': 'CSS Columns', 'is_correct': False},
                                 {'text': 'CSS Table', 'is_correct': False},
                             ]},
                            {'text': 'Como criar animação?',
                             'answers': [
                                 {'text': '@keyframes nome { ... }', 'is_correct': True},
                                 {'text': '@animation nome { ... }', 'is_correct': False},
                                 {'text': '@keyframe nome { ... }', 'is_correct': False},
                                 {'text': '@animate nome { ... }', 'is_correct': False},
                             ]},
                        ]
                    },
                ]
            },
            {
                'name': 'API RESTful com Python',
                'description': 'Crie APIs RESTful profissionais usando Django REST Framework. Autenticação, paginação e documentação automática.',
                'price': '129.90',
                'time': '40 horas',
                'videos': [
                    {'title': 'Fundamentos REST', 'url': 'https://www.youtube.com/embed/SLwpqD8n3d0', 'time': '1h 30min'},
                    {'title': 'Django REST Framework Setup', 'url': 'https://www.youtube.com/embed/TmsD03x9O4s', 'time': '1h 45min'},
                    {'title': 'Autenticação e Permissões', 'url': 'https://www.youtube.com/embed/c-QsfbznSXE', 'time': '1h 45min'},
                ],
                'materials': [
                    {'title': 'DRF Complete Guide.pdf', 'url': 'https://example.com/drf-guide.pdf'},
                    {'title': 'API Project Template', 'url': 'https://example.com/drf-template.zip'},
                    {'title': 'OpenAPI Spec Example', 'url': 'https://example.com/openapi.json'},
                ],
                'quizzes': [
                    {
                        'title': 'Quiz - REST API Design',
                        'questions': [
                            {'text': 'Qual HTTP method cria recurso?',
                             'answers': [
                                 {'text': 'POST', 'is_correct': True},
                                 {'text': 'GET', 'is_correct': False},
                                 {'text': 'PUT', 'is_correct': False},
                                 {'text': 'DELETE', 'is_correct': False},
                             ]},
                            {'text': 'O que significa RESTful?',
                             'answers': [
                                 {'text': 'Representational State Transfer', 'is_correct': True},
                                 {'text': 'Remote External Server Transfer', 'is_correct': False},
                                 {'text': 'Real Time Server Function', 'is_correct': False},
                                 {'text': 'Request External Service', 'is_correct': False},
                             ]},
                            {'text': 'Qual status code para sucesso?',
                             'answers': [
                                 {'text': '200', 'is_correct': True},
                                 {'text': '404', 'is_correct': False},
                                 {'text': '500', 'is_correct': False},
                                 {'text': '403', 'is_correct': False},
                             ]},
                            {'text': 'O que é Serializer no DRF?',
                             'answers': [
                                 {'text': 'Converte dados Python para JSON e vice-versa', 'is_correct': True},
                                 {'text': 'Um tipo de banco de dados', 'is_correct': False},
                                 {'text': 'Uma view', 'is_correct': False},
                                 {'text': 'Uma URL pattern', 'is_correct': False},
                             ]},
                        ]
                    },
                ]
            },
            {
                'name': 'Docker e Containerização',
                'description': 'Aprenda Docker para containerizar suas aplicações. Crie ambientes consistentes do desenvolvimento até produção.',
                'price': '109.90',
                'time': '30 horas',
                'videos': [
                    {'title': 'Introdução a Docker', 'url': 'https://www.youtube.com/embed/wi-MGiAZNMw', 'time': '1h 20min'},
                    {'title': 'Dockerfile e Images', 'url': 'https://www.youtube.com/embed/sUZxIWDUicA', 'time': '1h 45min'},
                    {'title': 'Docker Compose', 'url': 'https://www.youtube.com/embed/Qw9zlE3t8Ko', 'time': '1h 30min'},
                ],
                'materials': [
                    {'title': 'Docker Handbook.pdf', 'url': 'https://example.com/docker-handbook.pdf'},
                    {'title': 'Docker Compose Examples', 'url': 'https://example.com/compose-examples.zip'},
                    {'title': 'Best Practices Guide', 'url': 'https://example.com/docker-best-practices.pdf'},
                ],
                'quizzes': [
                    {
                        'title': 'Quiz - Docker Essentials',
                        'questions': [
                            {'text': 'O que é um Docker Image?',
                             'answers': [
                                 {'text': 'Template para criar containers', 'is_correct': True},
                                 {'text': 'Um arquivo de imagem', 'is_correct': False},
                                 {'text': 'Um servidor', 'is_correct': False},
                                 {'text': 'Um banco de dados', 'is_correct': False},
                             ]},
                            {'text': 'Qual arquivo define a imagem?',
                             'answers': [
                                 {'text': 'Dockerfile', 'is_correct': True},
                                 {'text': 'docker.yml', 'is_correct': False},
                                 {'text': 'image.docker', 'is_correct': False},
                                 {'text': 'config.docker', 'is_correct': False},
                             ]},
                            {'text': 'O que é Docker Compose?',
                             'answers': [
                                 {'text': 'Ferramenta para orquestrar múltiplos containers', 'is_correct': True},
                                 {'text': 'Um tipo de container', 'is_correct': False},
                                 {'text': 'Uma imagem oficial', 'is_correct': False},
                                 {'text': 'Um repositório', 'is_correct': False},
                             ]},
                            {'text': 'Como executar um container?',
                             'answers': [
                                 {'text': 'docker run image-name', 'is_correct': True},
                                 {'text': 'docker start image-name', 'is_correct': False},
                                 {'text': 'docker execute image-name', 'is_correct': False},
                                 {'text': 'docker launch image-name', 'is_correct': False},
                             ]},
                        ]
                    },
                ]
            },
            {
                'name': 'Testes Unitários e TDD',
                'description': 'Aprenda Test Driven Development e como escrever testes de qualidade. Crie código mais confiável e manutenível.',
                'price': '99.90',
                'time': '28 horas',
                'videos': [
                    {'title': 'Fundamentos de Testing', 'url': 'https://www.youtube.com/embed/-EadI39OLsY', 'time': '1h 30min'},
                    {'title': 'Testes com pytest', 'url': 'https://www.youtube.com/embed/bbp_849-RZ4', 'time': '1h 45min'},
                    {'title': 'Test Driven Development', 'url': 'https://www.youtube.com/embed/B1J6Yx3T3fE', 'time': '1h 45min'},
                ],
                'materials': [
                    {'title': 'Testing Guide.pdf', 'url': 'https://example.com/testing-guide.pdf'},
                    {'title': 'Test Examples', 'url': 'https://example.com/test-examples.zip'},
                    {'title': 'Mocking Patterns', 'url': 'https://example.com/mocking-patterns.pdf'},
                ],
                'quizzes': [
                    {
                        'title': 'Quiz - Testing Basics',
                        'questions': [
                            {'text': 'O que é um teste unitário?',
                             'answers': [
                                 {'text': 'Teste de uma unidade de código isolada', 'is_correct': True},
                                 {'text': 'Teste da aplicação toda', 'is_correct': False},
                                 {'text': 'Teste com usuários reais', 'is_correct': False},
                                 {'text': 'Teste de performance', 'is_correct': False},
                             ]},
                            {'text': 'O que significa TDD?',
                             'answers': [
                                 {'text': 'Test Driven Development', 'is_correct': True},
                                 {'text': 'Testing Data Development', 'is_correct': False},
                                 {'text': 'Technical Design Documentation', 'is_correct': False},
                                 {'text': 'Test Digital Design', 'is_correct': False},
                             ]},
                            {'text': 'Qual biblioteca para testes em Python?',
                             'answers': [
                                 {'text': 'pytest', 'is_correct': True},
                                 {'text': 'testing', 'is_correct': False},
                                 {'text': 'testify', 'is_correct': False},
                                 {'text': 'assertions', 'is_correct': False},
                             ]},
                            {'text': 'O que é um mock?',
                             'answers': [
                                 {'text': 'Objeto fake para simular comportamento', 'is_correct': True},
                                 {'text': 'Um tipo de teste', 'is_correct': False},
                                 {'text': 'Uma função real', 'is_correct': False},
                                 {'text': 'Um erro de teste', 'is_correct': False},
                             ]},
                        ]
                    },
                ]
            },
        ]

        # Create courses
        for course_data in courses_data:
            course = Course.objects.create(
                name=course_data['name'],
                description=course_data['description'],
                price=course_data['price'],
                time=course_data['time'],
            )

            # Create text content
            TextContentCoursePage.objects.create(
                course=course,
                title=f"Boas-vindas a {course_data['name']}",
                content=f"Bem-vindo ao curso {course_data['name']}! Este é um curso completo que cobrirá todos os aspectos importantes do tema. Você aprenderá desde os fundamentos até técnicas avançadas. Prepare-se para uma jornada de aprendizado empolgante!"
            )

            # Create videos
            for video in course_data['videos']:
                VideoCourse.objects.create(
                    course=course,
                    title=video['title'],
                    video_url=video['url'],
                    time=video['time'],
                )

            # Create materials
            for material in course_data['materials']:
                CourseMaterial.objects.create(
                    course=course,
                    title=material['title'],
                    file_url=material['url'],
                )

            # Create quizzes
            for quiz_data in course_data['quizzes']:
                quiz = Quiz.objects.create(
                    course=course,
                    title=quiz_data['title'],
                )

                # Create quiz questions and answers
                for question_data in quiz_data['questions']:
                    question = QuizQuestion.objects.create(
                        quiz=quiz,
                        text=question_data['text'],
                    )

                    # Create answers
                    for answer_data in question_data['answers']:
                        QuizAnswer.objects.create(
                            question=question,
                            text=answer_data['text'],
                            is_correct=answer_data['is_correct'],
                        )

        self.stdout.write(
            self.style.SUCCESS(
                '✅ 10 cursos completos foram criados com sucesso!\n'
                '   - Cada curso contém 3 vídeos\n'
                '   - Cada curso contém 2-3 materiais\n'
                '   - Cada curso contém quizes com 4 questões'
            )
        )
