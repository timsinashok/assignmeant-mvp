from ai71 import AI71 

AI71_API_KEY = "api71-api-fd38a0d8-5cc4-445f-9fe9-eeaff4baa17d"


def get_response(prompt):
    for chunk in AI71(AI71_API_KEY).chat.completions.create(
        model="tiiuae/falcon-180b-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        stream=True,
    ):
        if chunk.choices[0].delta.content:
            return chunk.choices[0].delta.content
        



