from openai import OpenAI

from main.settings import GPT_APIKEY


class ChatGPT:

    def __init__(self, instructions: list = list):
        self.client = OpenAI(
            api_key=GPT_APIKEY
        )

        self.instructions = instructions
        self.messages = []

    def set_instruction(self, instruction: str,  role: str = "system"):
        self.instructions.append(
            {"role": role, "content": instruction}
        )

    def clear_messages(self):
        self.messages = []
        self.messages += self.instructions

    def send_message(self, message):
        self.messages.append(
            {"role": "user", "content": message}
        )

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.messages,
        ).to_dict()

        answer = response["choices"][0]["message"]["content"]
        self.messages.append(
            {"role": "assistant", "content": answer}
        )
        return answer
