from ai71 import AI71 
from ML_zone.config import read_api_config

# config_file = 'ML_zone/config.txt'
# client = AI71(read_api_config(config_file))


def get_response(prompt):
    config_file = 'ML_zone/config.txt'
    client = AI71(read_api_config(config_file))
    response = client.chat.completions.create(
        model="tiiuae/falcon-180b-chat",
        messages=prompt
    )

    return response.choices[0].message.content

        



