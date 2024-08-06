from ai71 import AI71 
from ML_zone.config import read_api_config

config_file = 'ML_zone/config.txt'
client = AI71(read_api_config(config_file))


def get_response(prompt):
    for chunk in client.chat.completions.create(
        model="tiiuae/falcon-180b-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        stream=True,
    ):
        if chunk.choices[0].delta.content:
            return chunk.choices[0].delta.content
        



