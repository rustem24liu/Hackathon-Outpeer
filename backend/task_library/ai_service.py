import os
import json
import openai
from django.conf import settings

# Инициализация API ключа
openai.api_key = settings.OPENAI_API_KEY

def get_ai_response(messages):
    """
    Получить ответ от ChatGPT API
    
    Args:
        messages: Список словарей {"role": "...", "content": "..."} с историей сообщений
    
    Returns:
        str: Текстовый ответ от модели
    """
    try:
        # Делаем запрос к API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Можно использовать "gpt-4" при наличии доступа
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
        )
        
        # Возвращаем текст ответа
        return response.choices[0].message.content
    except Exception as e:
        # Логирование ошибки
        print(f"Ошибка при обращении к OpenAI API: {str(e)}")
        raise Exception(f"Не удалось получить ответ от ИИ: {str(e)}")