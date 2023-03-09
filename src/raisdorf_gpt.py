import utility.chatgpt as chatgpt
import random
from settings import RaisdorfUser

RAISDORFGPT_CHANNEL_IDS = {
    985221327722016841, # MelvinsBaustelle - general
    982391359103180873, # CAU-Elite - general
    1065604359100047472, # CAU-Elite - memes
    1039643607747018872, # CAU-Elite - OS
    1041461676479881318, # CAU-Elite - DeklProg
    1052004758451392662, # CAU-Elite - Weitere Kunst
    1067487318337925170  # CAU-Elite - Chat-GPT Witze
}
RAISDORFGPT_PROBABILITY: float = 0.3

RAISDORFGPT_PROMPT: str = 'Du bist DerBusNachRaisdorf, eine KI, die auf dem Discord-Server CAU-Elite lebt und immer sehr geschwollen spricht. Antworte immer als DerBusNachRaisdorf, aber ohne vorangehendes DerBusNachRaisdorf:'

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

    