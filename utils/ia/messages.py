def create_exercise(quant, language):
    return (
        f"Crie {quant} pergunta(s) em {language} de multipla escolha em sobre o texto informado, "
        f"no formato JSON especificado anteriormente. Cada pergunta terá 5 opções e é importante que não esqueça de incluir um"
        f" campo para informar a qual o idioma da pergunta (inglês ou português) e de elaborar "
        f"perguntas fáceis e díficeis, indicando qual o nível de dificuldade da questão, "
        f"como um dos campos da questão no arquivo JSON. As opções devem ser um dicionário onde a chave será o "
        f"identificador da resposta e pode ser de 'a' até 'e'. A resposta correta será a chave da resposta indicada no campo awnser."

    )


def translate_text(text: str, language: str = "português"):
    return (
        f"Traduza o texto a seguir para o {language}, usando a forma mais comum e falada pelos nativos. Texto: '{text}'"
    )


