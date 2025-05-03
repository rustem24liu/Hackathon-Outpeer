import os
import json
import requests
import streamlit as st

# URL для API
API_BASE_URL = "http://localhost:8000/api/"

def get_api_url(endpoint):
    """Получить полный URL для API endpoint"""
    return f"{API_BASE_URL}{endpoint}"

def get_token():
    """Получить токен из файла или None, если токен не найден"""
    try:
        with open('.token', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def save_token(token):
    """Сохранить токен в файл"""
    if token:
        with open('.token', 'w') as f:
            f.write(token)
    else:
        try:
            os.remove('.token')
        except FileNotFoundError:
            pass

def login(username, password):
    """Выполнить вход и получить токен авторизации"""
    try:
        # В простом случае используем BasicAuth
        response = requests.post(
            get_api_url("auth/login/"),
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            return response.json().get("token")
        return None
    except Exception as e:
        print(f"Login error: {str(e)}")
        return None

def api_request(endpoint, method="GET", data=None, params=None, auth_required=True):
    """Выполнить запрос к API с обработкой ошибок"""
    url = get_api_url(endpoint)
    headers = {}
    
    if auth_required and st.session_state.is_authenticated:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code >= 400:
            error_msg = f"API error ({response.status_code}): "
            try:
                error_data = response.json()
                error_msg += json.dumps(error_data)
            except:
                error_msg += response.text
            
            raise Exception(error_msg)
        
        if response.status_code != 204:  # No content
            return response.json()
        return None
    except Exception as e:
        print(f"API request error ({method} {endpoint}): {str(e)}")
        raise

# Функции для работы с API

def get_categories():
    """Получить список категорий"""
    try:
        return api_request("categories/", auth_required=False)
    except Exception:
        return []

def get_tasks(search_query=None):
    """Получить список заданий"""
    params = {}
    if search_query:
        params["search"] = search_query
    
    try:
        return api_request("tasks/", params=params, auth_required=False)
    except Exception:
        return []

def get_task(task_id):
    """Получить детали задания по ID"""
    try:
        return api_request(f"tasks/{task_id}/", auth_required=False)
    except Exception as e:
        st.error(f"Ошибка при получении задания: {str(e)}")
        return None

def get_solutions(task_id=None):
    """Получить список решений, опционально для конкретного задания"""
    endpoint = f"tasks/{task_id}/solutions/" if task_id else "solutions/"
    
    try:
        return api_request(endpoint, auth_required=False)
    except Exception:
        return []

def get_solution(solution_id):
    """Получить детали решения по ID"""
    try:
        return api_request(f"solutions/{solution_id}/", auth_required=False)
    except Exception as e:
        st.error(f"Ошибка при получении решения: {str(e)}")
        return None

def create_task(title, description, difficulty, category):
    """Создать новое задание"""
    data = {
        "title": title,
        "description": description,
        "difficulty": difficulty,
        "category": category
    }
    
    return api_request("tasks/", method="POST", data=data)

def create_solution(task_id, code, explanation, is_ai_generated=False, steps=None):
    """Создать новое решение"""
    data = {
        "task": task_id,
        "code": code,
        "explanation": explanation,
        "is_ai_generated": is_ai_generated
    }
    
    if steps:
        data["steps"] = steps
    
    return api_request("solutions/", method="POST", data=data)

def get_ai_chats():
    """Получить список чатов с ИИ-ассистентом"""
    try:
        return api_request("ai-chats/")
    except Exception:
        return []

def get_ai_chat(chat_id):
    """Получить детали чата с ИИ-ассистентом по ID"""
    try:
        return api_request(f"ai-chats/{chat_id}/")
    except Exception as e:
        st.error(f"Ошибка при получении чата: {str(e)}")
        return {"title": "Ошибка", "messages": []}

def send_ai_message(chat_id, message):
    """Отправить сообщение в чат с ИИ и получить ответ"""
    data = {"message": message}
    return api_request(f"ai-chats/{chat_id}/add_message/", method="POST", data=data)

def login(username, password):
    try:
        response = requests.post(
            get_api_url("auth/login/"),
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            return response.json().get("token")
        return None
    except Exception as e:
        print(f"Login error: {str(e)}")
        return None
        