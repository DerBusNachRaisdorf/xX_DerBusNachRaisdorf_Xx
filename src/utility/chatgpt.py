import requests
import json


CHATGPT_API_URL: str = 'https://chatgpt-api.shn.hk/v1/'
CHATGPT_MESSAGE_HISTORY: int = 24


class ChatGPTSession:
    def __init__(self, instruction: str = None):
        self.messages: list[dict[str, str]] = []
        if instruction:
            self.add_system_message(instruction)

    def ask(self, message: str) -> str:
        self.add_user_message(message)
        return self.request_response()

    def add_user_message(self, content: str):
        self.__append_message({"role": "user", "content": content})

    def add_system_message(self, content: str):
        self.__append_message({"role": "system", "content": content})

    def request_response(self) -> str:
        response = ChatGPTSession.__chat_gpt_request(self.messages)
        if response:
            self.__append_message({"role": "assistant", "content": response['content']})
            return response['content']
        return None

    def __append_message(self, message: dict[str, str]):
        self.messages.append(message)
        if len(message) >= CHATGPT_MESSAGE_HISTORY:
            self.messages.pop(1) # not 0 because 0 is the initial instruction on how chatgpt should act.

    @staticmethod
    def __chat_gpt_request(messages: list[dict[str, str]]) -> str:
        headers: dict = {'content-type': 'application/json'}
        payload: dict = {
            "model": "gpt-3.5-turbo",
            "messages": messages
        }
        response_json = requests.post(CHATGPT_API_URL, data=json.dumps(payload), headers=headers).text.strip(' ').strip('\t')

        try:
            response = json.loads(response_json)
            return response['choices'][0]['message']
        except Exception as e:
            raise Exception(f'Unexpected ChatGPT answer: \n{response_json}\nException: {e}')

    def to_json(self) -> str:
        return json.dumps(self.messages)
    
    def load_json(self, json: str):
        self.messages = json.loads(json)


if __name__ == '__main__':
    chat_gpt = ChatGPTSession('Du bist Otto, eine KI, die immer sehr elaboriert und geschwollen spricht.')
    while True:
        i = input()
        print(chat_gpt.ask(i))
