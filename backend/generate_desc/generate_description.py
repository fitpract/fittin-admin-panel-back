import re

from g4f.client import Client
from g4f.Provider import Blackbox
from g4f.providers.retry_provider import RetryProvider
from g4f import debug
client = Client(
    provider=RetryProvider([Blackbox],
                            single_provider_retry= True)
)


def generate_product_description(product_name):
    debug.logging = True 
    debug.version_check = False 
    """
    Генерирует описание продукта с использованием модели g4f.

    product_name (str): Название продукта.

    return: str: Сгенерированное описание продукта.
    """

    response = client.chat.completions.create(
        model="",
        messages=[{"role": "user",
                   "content": f"Сгенерируй описание для товара на русском примерно в 15 слов, только описание текст: {product_name}"}],
    )
    description = response.choices[0].message.content
    pattern = r"[^а-яА-Я\s.,!?;:\"\'\[\]\(\)\{\}]+"

    description = re.sub(pattern, '', description)
    start = description.find('"')
    end = description.find('"', start + 1)
    if start != -1 and end != -1:
        description = description[start + 1:end]
    if description.startswith('.'):
        description = description[1:]

    return description
