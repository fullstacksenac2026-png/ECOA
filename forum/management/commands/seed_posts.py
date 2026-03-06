import random
from django.core.management.base import BaseCommand
from forum.models import Post, Comment, CommentLike, CommentDislike
from authorization.models import User


class Command(BaseCommand):
    help = "Cria posts ambientais com comentários, likes e dislikes"

    def handle(self, *args, **kwargs):

        user = User.objects.first()

        if not user:
            self.stdout.write(self.style.ERROR("Crie um usuário antes de rodar a seed"))
            return

        posts_data = [
            {
                "title": "A importância da preservação da Amazônia",
                "content": "A Amazônia é essencial para o equilíbrio climático global."
            },
            {
                "title": "Poluição dos oceanos",
                "content": "Milhões de toneladas de plástico são despejadas nos oceanos todos os anos."
            },
            {
                "title": "Energia solar no Brasil",
                "content": "O Brasil tem grande potencial para geração de energia solar."
            },
            {
                "title": "Desmatamento e mudanças climáticas",
                "content": "O desmatamento acelera o aquecimento global."
            },
            {
                "title": "Importância da reciclagem",
                "content": "Reciclar reduz o lixo e preserva recursos naturais."
            },
            {
                "title": "Crise da água no mundo",
                "content": "Muitos países enfrentam escassez de água potável."
            },
            {
                "title": "Cidades sustentáveis",
                "content": "Planejamento urbano sustentável melhora a qualidade de vida."
            },
            {
                "title": "Proteção da fauna brasileira",
                "content": "Animais silvestres estão ameaçados pela destruição de habitats."
            },
            {
                "title": "Impacto dos combustíveis fósseis",
                "content": "A queima de petróleo e carvão aumenta a emissão de CO2."
            },
            {
                "title": "Agricultura sustentável",
                "content": "Práticas agrícolas sustentáveis ajudam a preservar o solo."
            }
        ]

        comments_data = [
            "Esse tema é muito importante!",
            "Precisamos falar mais sobre isso.",
            "A educação ambiental é essencial.",
            "Infelizmente muitas pessoas ignoram esse problema.",
            "Ótima reflexão sobre o meio ambiente.",
            "Isso deveria ser prioridade dos governos.",
            "Precisamos agir agora.",
            "Muito bom ver discussões assim.",
        ]

        for post_data in posts_data:

            post = Post.objects.create(
                user=user,
                title=post_data["title"],
                content=post_data["content"]
            )

            # cria comentários
            for _ in range(random.randint(3, 6)):

                comment = Comment.objects.create(
                    post=post,
                    content=random.choice(comments_data)
                )

                # likes
                for i in range(random.randint(0, 5)):
                    CommentLike.objects.create(
                        post=post,
                        comment=comment,
                        user=f"user_like_{i}"
                    )

                # dislikes
                for i in range(random.randint(0, 2)):
                    CommentDislike.objects.create(
                        post=post,
                        comment=comment,
                        user=f"user_dislike_{i}"
                    )

        self.stdout.write(self.style.SUCCESS("Seeds criadas com sucesso!"))