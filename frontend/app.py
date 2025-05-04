import streamlit as st
import requests
import pandas as pd
import os
import json
from dotenv import load_dotenv
import openai


load_dotenv()


BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://backend:8000/api/')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')


openai.api_key = OPENAI_API_KEY


st.set_page_config(
    page_title="Визуальная библиотека решений",  #Robert это ваша часть
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


def get_token(username, password):
    """Получение токена аутентификации"""
    try:
        response = requests.post(
            f"{BACKEND_API_URL}token/", 
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Ошибка для аутентификации: {str(e)}")
        return None

def api_request(endpoint, method='GET', data=None, params=None, token=None):
    """Выполнение запроса к API"""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == 'GET':
            response = requests.get(
                f"{BACKEND_API_URL}{endpoint}", 
                headers=headers,
                params=params
            )
        elif method == 'POST':
            response = requests.post(
                f"{BACKEND_API_URL}{endpoint}", 
                headers=headers,
                json=data
            )
        elif method == 'PUT':
            response = requests.put(
                f"{BACKEND_API_URL}{endpoint}", 
                headers=headers,
                json=data
            )
        elif method == 'DELETE':
            response = requests.delete(
                f"{BACKEND_API_URL}{endpoint}", 
                headers=headers
            )
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"Ошибка API: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Ошибка запроса: {str(e)}")
        return None

def ask_chatgpt(prompt, task_context=""):
    """Функция для запроса к ChatGPT API через бэкенд Rustem это ваша часть"""
    token = st.session_state.get('token')
    if not token:
        st.error("Необходима авторизация для использования ChatGPT")
        return None
    
    try:
        response = api_request(
            "chatgpt-assistance/", 
            method='POST', 
            data={"prompt": prompt, "task_context": task_context},
            token=token
        )
        if response:
            return response.get("answer")
        return None
    except Exception as e:
        st.error(f"Ошибка при запросе к ChatGPT: {str(e)}")
        return None

# Функция инициализации состояния сессии
def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"

def login_page():
    """Страница авторизации"""
    st.title("Авторизация")
    
    with st.form("login_form"):
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type="password")
        submit = st.form_submit_button("Войти")
        
        if submit:
            if username and password:
                token_data = get_token(username, password)
                if token_data and 'access' in token_data:
                    st.session_state.token = token_data['access']
                    st.session_state.authenticated = True
                    st.session_state.user_info = {"username": username}
                    st.success("Авторизация прошла успешно!")
                    st.rerun()
                else:
                    st.error("Неверное имя пользователя или пароль")
            else:
                st.error("Введите имя пользователя и пароль")

def render_home():
    """Домашняя страница"""
    st.title("📚 Визуальная библиотека решений и воспроизведений заданий")
    
    st.markdown("""
    ## Добро пожаловать в визуальную библиотеку решений! 
    
    Этот инструмент предназначен для:
    * 🧩 Сбора и категоризации различных заданий
    * 💡 Предоставления проверенных решений
    * 🔄 Воспроизведения решений для проверки их корректности
    * 🤖 Получения помощи от ChatGPT при решении сложных задач
    
    ### Начните работу:
    * Просмотрите доступные задания и их решения
    * Создайте собственное задание или решение
    * Проверьте решения, воспроизведя их
    * Используйте ИИ-ассистента для помощи
    
    """)
    
    # Недавние задания
    st.subheader("📋 Недавние задания")
    tasks = api_request("tasks/", params={"ordering": "-created_at", "limit": 5}, token=st.session_state.token)
    
    if tasks and 'results' in tasks:
        for task in tasks['results']:
            with st.expander(f"{task['title']} (Сложность: {task['complexity']}/10)"):
                st.write(task['description'])
                st.write(f"Категория: {task.get('category_name', 'Не указано')}")
                st.write(f"Решений: {task.get('solutions_count', 0)}")
                st.button("Подробнее", key=f"task_{task['id']}", 
                          on_click=lambda id=task['id']: set_page(f"task_detail_{id}"))
    
    # Недавние решения
    st.subheader("💡 Недавние решения")
    solutions = api_request("solutions/", params={"ordering": "-created_at", "limit": 5}, token=st.session_state.token)
    
    if solutions and 'results' in solutions:
        for solution in solutions['results']:
            with st.expander(f"{solution['title']} ({solution.get('task_title', 'Не указано')})"):
                st.write(solution['description'][:200] + "..." if len(solution['description']) > 200 else solution['description'])
                st.write(f"Воспроизведений: {solution.get('reproductions_count', 0)}")
                st.button("Подробнее", key=f"solution_{solution['id']}", 
                          on_click=lambda id=solution['id']: set_page(f"solution_detail_{id}"))

def render_tasks():
    """Страница со списком заданий"""
    st.title("📋 Задания")
    
    # Фильтры
    col1, col2, col3 = st.columns(3)
    with col1:
        categories = api_request("categories/", token=st.session_state.token)
        category_options = ["Все"] + [cat['name'] for cat in categories] if categories else ["Все"]
        selected_category = st.selectbox("Категория", category_options)
    
    with col2:
        complexity = st.slider("Сложность", 1, 10, (1, 10))
    
    with col3:
        search_query = st.text_input("Поиск по заданиям")
    
    # Параметры запроса
    params = {"ordering": "-created_at"}
    if selected_category != "Все" and categories:
        category_id = next((cat['id'] for cat in categories if cat['name'] == selected_category), None)
        if category_id:
            params["category"] = category_id
    
    if complexity:
        params["complexity__gte"] = complexity[0]
        params["complexity__lte"] = complexity[1]
    
    if search_query:
        params["search"] = search_query
    
    # Получение заданий
    tasks = api_request("tasks/", params=params, token=st.session_state.token)
    
    if tasks and 'results' in tasks:
        for task in tasks['results']:
            with st.expander(f"{task['title']} (Сложность: {task['complexity']}/10)"):
                st.write(task['description'])
                st.write(f"Категория: {task.get('category_name', 'Не указано')}")
                st.write(f"Решений: {task.get('solutions_count', 0)}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.button("Подробнее", key=f"task_detail_{task['id']}", 
                              on_click=lambda id=task['id']: set_page(f"task_detail_{id}"))
                with col2:
                    st.button("Просмотр решений", key=f"task_solutions_{task['id']}", 
                              on_click=lambda id=task['id']: set_page(f"task_solutions_{id}"))
    else:
        st.info("Задания не найдены или произошла ошибка загрузки.")

def render_solutions():
    """Страница со списком решений"""
    st.title("💡 Решения")
    
    # Фильтры
    search_query = st.text_input("Поиск по решениям")
    
    # Параметры запроса
    params = {"ordering": "-created_at"}
    if search_query:
        params["search"] = search_query
    
    # Получение решений
    solutions = api_request("solutions/", params=params, token=st.session_state.token)
    
    if solutions and 'results' in solutions:
        for solution in solutions['results']:
            with st.expander(f"{solution['title']} ({solution.get('task_title', 'Не указано')})"):
                st.write(solution['description'][:200] + "..." if len(solution['description']) > 200 else solution['description'])
                st.write(f"Воспроизведений: {solution.get('reproductions_count', 0)}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.button("Подробнее", key=f"sol_detail_{solution['id']}", 
                              on_click=lambda id=solution['id']: set_page(f"solution_detail_{id}"))
                with col2:
                    st.button("Просмотр воспроизведений", key=f"sol_reproductions_{solution['id']}", 
                              on_click=lambda id=solution['id']: set_page(f"solution_reproductions_{id}"))
    else:
        st.info("Решения не найдены или произошла ошибка загрузки.")

def render_ai_assistant():
    """Страница ИИ-ассистента"""
    st.title("🤖 ChatGPT Ассистент")
    
    st.markdown("""
    ## Используйте мощь искусственного интеллекта для решения задач
    
    ChatGPT может помочь вам:
    * Разобраться в условии задания
    * Получить подсказки для решения
    * Проверить правильность вашего решения
    * Объяснить сложные концепции
    """)
    
    # Выбор задания для контекста (опционально)
    st.subheader("Выберите задание для контекста (необязательно)")
    tasks = api_request("tasks/", token=st.session_state.token)
    task_options = ["Без контекста"] + [task['title'] for task in tasks['results']] if tasks and 'results' in tasks else ["Без контекста"]
    selected_task = st.selectbox("Задание", task_options)
    
    task_context = ""
    if selected_task != "Без контекста" and tasks and 'results' in tasks:
        task = next((t for t in tasks['results'] if t['title'] == selected_task), None)
        if task:
            task_context = f"{task['title']}\n\n{task['description']}"
            st.info(f"Выбрано задание: {task['title']}")
    
    # Форма для запроса
    st.subheader("Задайте вопрос ассистенту")
    with st.form("ai_assistant_form"):
        prompt = st.text_area("Ваш вопрос", height=150)
        submit = st.form_submit_button("Отправить запрос")
        
        if submit and prompt:
            with st.spinner("Получение ответа от ChatGPT..."):
                answer = ask_chatgpt(prompt, task_context)
                if answer:
                    st.session_state.ai_answer = answer
                    st.rerun()
    
    # Отображение ответа
    if 'ai_answer' in st.session_state:
        st.subheader("Ответ ассистента:")
        st.markdown(st.session_state.ai_answer)
        
        # Опция сохранения ответа
        if st.button("Сохранить этот ответ как решение"):
            if selected_task != "Без контекста" and tasks and 'results' in tasks:
                task = next((t for t in tasks['results'] if t['title'] == selected_task), None)
                if task:
                    st.session_state.create_solution_task_id = task['id']
                    st.session_state.create_solution_ai_answer = st.session_state.ai_answer
                    st.session_state.current_page = "create_solution"
                    st.rerun()
            else:
                st.warning("Для сохранения решения необходимо выбрать задание из контекста")

def set_page(page):
    """Функция для смены страницы"""
    st.session_state.current_page = page
    st.rerun()

def render_sidebar():
    """Отрисовка боковой панели"""
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150.png?text=VL", width=150)
        st.title("Навигация")
        
        if st.session_state.authenticated:
            st.write(f"Пользователь: {st.session_state.user_info['username']}")
            
            st.button("🏠 Главная", on_click=lambda: set_page("home"))
            st.button("📋 Задания", on_click=lambda: set_page("tasks"))
            st.button("💡 Решения", on_click=lambda: set_page("solutions"))
            st.button("🔄 Воспроизведения", on_click=lambda: set_page("reproductions"))
            st.button("🤖 ИИ-ассистент", on_click=lambda: set_page("ai_assistant"))
            
            st.divider()
            st.button("➕ Создать задание", on_click=lambda: set_page("create_task"))
            
            st.divider()
            if st.button("Выйти"):
                st.session_state.authenticated = False
                st.session_state.token = None
                st.session_state.user_info = None
                st.rerun()
        else:
            st.info("Для доступа к функциям необходимо авторизоваться")

def render_page():
    """Отрисовка текущей страницы"""
    current_page = st.session_state.current_page
    
    if not st.session_state.authenticated:
        login_page()
        return
    
    # Маршрутизация страниц
    if current_page == "home":
        render_home()
    elif current_page == "tasks":
        render_tasks()
    elif current_page == "solutions":
        render_solutions()
    elif current_page == "reproductions":
        st.title("🔄 Воспроизведения")
        st.info("Раздел находится в разработке")
    elif current_page == "ai_assistant":
        render_ai_assistant()
    elif current_page == "create_task":
        st.title("➕ Создание задания")
        st.info("Функция создания задания находится в разработке")
    elif current_page.startswith("task_detail_"):
        task_id = current_page.split("_")[-1]
        st.title("Детали задания")
        st.write(f"Загрузка информации о задании {task_id}...")
        # Здесь будет отображение деталей задания
    elif current_page.startswith("solution_detail_"):
        solution_id = current_page.split("_")[-1]
        st.title("Детали решения")
        st.write(f"Загрузка информации о решении {solution_id}...")
        # Здесь будет отображение деталей решения
    else:
        st.error("Страница не найдена")
        set_page("home")

# Основная функция
def main():
    init_session_state()
    render_sidebar()
    render_page()

if __name__ == "__main__":
    main()
