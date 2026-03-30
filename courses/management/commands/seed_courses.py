import random
from django.core.management.base import BaseCommand
from courses.models import Course, Section, Lesson

class Command(BaseCommand):
    help = 'Popula o banco de dados com 10 cursos diferentes'

    def handle(self, *args, **kwargs):
        courses_data = [
            {
                "name": "Python para Iniciantes",
                "description": "Aprenda a linguagem de programação mais popular do mundo, do zero ao primeiro projeto. Este curso cobre desde variáveis e loops até funções e introdução à orientação a objetos.",
                "price": 149.90,
                "time": "20 horas",
                "rating": 4.8,
                "students_count": 1250
            },
            {
                "name": "Design Digital com Figma",
                "description": "Domine o Figma e crie interfaces incríveis para sites e aplicativos móveis. Aprenda sobre tipografia, paleta de cores, componentes e prototipação interativa.",
                "price": 199.00,
                "time": "15 horas",
                "rating": 4.9,
                "students_count": 850
            },
            {
                "name": "Marketing em Redes Sociais",
                "description": "Estratégias avançadas para crescer e vender no Instagram, TikTok e LinkedIn. Entenda algoritmos, criação de conteúdo e gestão de tráfego pago.",
                "price": 89.90,
                "time": "10 horas",
                "rating": 4.5,
                "students_count": 2100
            },
            {
                "name": "Gestão de Projetos Ágeis",
                "description": "Aprenda Scrum, Kanban e como liderar equipes de alta performance em ambientes dinâmicos. Conceitos de Sprints, Product Backlog e Daily Scrum.",
                "price": 299.00,
                "time": "25 horas",
                "rating": 4.7,
                "students_count": 450
            },
            {
                "name": "Desenvolvimento Web Full Stack",
                "description": "Crie aplicações completas usando HTML, CSS, JS, Node e React. O caminho completo para se tornar um desenvolvedor preparado para o mercado.",
                "price": 599.00,
                "time": "120 horas",
                "rating": 4.9,
                "students_count": 600
            },
            {
                "name": "Excel Avançado para Negócios",
                "description": "Domine tabelas dinâmicas, dashboards e automação com VBA. Transforme dados em informações estratégicas para tomada de decisão.",
                "price": 129.00,
                "time": "30 horas",
                "rating": 4.6,
                "students_count": 3200
            },
            {
                "name": "Edição de Vídeo Profissional",
                "description": "Aprenda a editar vídeos de alto impacto usando o Adobe Premiere Pro. Técnicas de corte, correção de cor, áudio e efeitos especiais.",
                "price": 249.00,
                "time": "40 horas",
                "rating": 4.8,
                "students_count": 780
            },
            {
                "name": "Fotografia Digital",
                "description": "Tire fotos melhores com sua DSLR ou smartphone. Dicas de luz, composição, foco e edição básica no Lightroom.",
                "price": 179.00,
                "time": "12 horas",
                "rating": 4.7,
                "students_count": 1100
            },
            {
                "name": "Inteligência Artificial na Prática",
                "description": "Entenda como usar ChatGPT, Midjourney e outras ferramentas de IA no dia a dia para aumentar sua produtividade e criatividade.",
                "price": 159.00,
                "time": "08 horas",
                "rating": 4.9,
                "students_count": 1500
            },
            {
                "name": "Vendas e Atendimento",
                "description": "Técnicas de persuasão, contorno de objeções e fidelização para encantar seus clientes e bater metas consistentemente.",
                "price": 75.00,
                "time": "06 horas",
                "rating": 4.4,
                "students_count": 2800
            }
        ]

        self.stdout.write(self.style.SUCCESS("Iniciando o seeding de cursos..."))

        for data in courses_data:
            course, created = Course.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "price": data["price"],
                    "time": data["time"],
                    "rating": data["rating"],
                    "students_count": data["students_count"]
                }
            )

            if created:
                self.stdout.write(f"Curso criado: {course.name}")
                # Criar seções e lições básicas para cada curso
                for i in range(1, 4):
                    section = Section.objects.create(
                        course=course,
                        title=f"Módulo {i}: Introdução ao {course.name}",
                        description=f"Nesta seção veremos os fundamentos de {course.name}.",
                        order=i
                    )
                    for j in range(1, 4):
                        Lesson.objects.create(
                            section=section,
                            title=f"Aula {j}: Conceitos de nível {j}",
                            description=f"Explicação detalhada sobre o tópico {j} do curso {course.name}.",
                            lesson_type='video' if j % 2 != 0 else 'text',
                            order=j,
                            duration_minutes=random.randint(5, 30)
                        )
            else:
                self.stdout.write(self.style.WARNING(f"Curso já existe: {course.name}"))

        self.stdout.write(self.style.SUCCESS("Seeding concluído com sucesso!"))
