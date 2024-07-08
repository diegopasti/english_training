import json

from utils.ia.base import ChatGPT
from utils.ia.messages import create_exercise, translate_text


class Teacher:

    def __init__(self):
        self.instructions = [
            {
                "role": "system",
                "content": "Você é um professor de inglês fluente, natural do Estados Unidos com muitos anos de "
                           "experiência no ensino do idioma para Brasileiros."
            },

            {
                "role": "system",
                "content": "Você é um professor prestativo com uma boa didática e comunicação simples mas correta"
                           " gramaticalmente."
            },

            {
                "role": "system",
                "content": "Você precisará criar questões sobre um determinado texto que serão usados como teste "
                           "avaliativo que poderá ser em português e inglês. Seja criativo e não repita perguntas, nem mesmo que sejam muito parecidas."
            },

            {
                "role": "system",
                "content": "Os exercicios que for criar precisa seguir um formato JSON e seguindo o seguinte padrão:"
                           "question = {'title': '', 'language':'', 'dificult': '',  'choices': {'a': 'primeira opção', 'b': 'segunda opção', 'c':'terceira opção', 'd':'quarta opção', 'e':'quinta opção'}}, 'correct': 'a'}"
            },

            {
                "role": "system",
                "content": "Os exercicios que irá criar precisa ter três níveis de dificuldade, 1 para o nível mais básico e 3 para o nível mais díficil."
                           "No nível 1 são perguntas bem objetivas e respostas bem objetivas, que avalia a compreensão mínima do texto e do assunto além do vocábulario."
                           f"No nível 2 são perguntas e respostas mais elaboradas, que exigem um nível maior de atenção e vocábulário, bem como uma visão mais profunda sobre o tema."
                           f"No nível 3 são perguntas e respostas complexas e demonstram que o aluno compreendeu o texto, compreendeu a pergunta e explora um pouco mais do vocabulário e da visão analítica e crítica sobre o tema. Podem ser incluido alguma informação que se relacione diretamente com o texto tornando o exercicio mais inteligente."
            },

            {
                "role": "system",
                "content": "Os exercícios de nível 1 precisamos avaliar que o aluno tenha compreendido minimamente o texto e utilizar um vocabulário mais comum. No nível mais difícil precisamos garantir que o aluno tenha compreendido perfeitamente o texto, inclusive quando as perguntas são mais complexas e correlacionam outros conhecimentos que podem complementar o assunto me questão."
            },
        ]

        self.ia = ChatGPT(self.instructions)

    def translate(self, text):
        message = translate_text(text)
        answer = self.ia.send_message(message)
        print("VEJA A RESPOSTA:", answer)

    def create_question(self, quant=15, language="inglês"):
        message = create_exercise(quant, language)
        answer = self.ia.send_message(message)

        print("VEJA A RESPOSTA:", answer)
        questions = json.loads(answer)
        print("VEJA AS QUESTOES:", questions)


if __name__ == "__main__":
    teacher = Teacher()

    message = """
    Europe sends a lot of waste to poor countries every year. Some of this is against the law.

    This illegal trade hurts the natural world. It helps criminals get rich. The EU wants to stop this and recycle more waste. New EU rules make it hard for countries to get waste. They must show that they can handle it right. They also stop sending plastic waste outside the EU.

    Italy has a new system which helps stop illegal waste trade. They check containers with false labels. Europe is recycling old cables. But now, Europe recycles only 12% of all waste. We need more rules and help to recycle more.
    """

    translation = teacher.translate(message)
    questions = teacher.create_question()
