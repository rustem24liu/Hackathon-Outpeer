import os
import json
from openai import OpenAI
from django.conf import settings

# Инициализация клиента API
client = OpenAI(api_key=settings.OPENAI_API_KEY)

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
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
        )
        
        # Возвращаем текст ответа
        return response.choices[0].message.content
    except Exception as e:
        # Логирование ошибки
        print(f"Ошибка при обращении к OpenAI API: {str(e)}")
        return f"Не удалось получить ответ от ИИ: {str(e)}"