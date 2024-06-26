def read_api_config(config_file):
    with open(config_file, 'r') as file:
        OPENAI_API_KEY = file.read().strip()
    return OPENAI_API_KEY
