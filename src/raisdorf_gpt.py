import utility.chatgpt as chatgpt
import random
from settings import RaisdorfUser

RAISDORFGPT_CHANNEL_IDS = {985221327722016841}
RAISDORFGPT_PROBABILITY: float = 0.3

RAISDORFGPT_PROMPT: str = 'Du bist DerBusNachRaisdorf, eine KI, die auf dem Discord-Server CAU-Elite lebt und immer sehr geschwollen spricht.'

def probability_check(probability: float):
    return random.uniform(0, 1) <= probability

class RaisdorfGPT:
    def __init__(self):
        self.chatgpt = chatgpt.ChatGPTSession(RAISDORFGPT_PROMPT)
    
    def on_message(self, message: str, sender: RaisdorfUser, channel_id: int, bot_mentioned: bool=False) -> str:
        if channel_id not in RAISDORFGPT_CHANNEL_IDS:
            return None

        user_message_string: str = f'{sender.name}: {message}'
        if (probability_check(RAISDORFGPT_PROBABILITY)) or bot_mentioned:
            response = self.chatgpt.ask(user_message_string)
            return response
        else:
            self.chatgpt.add_user_message(user_message_string)
            return None

    