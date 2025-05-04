import streamlit as st
import requests
<<<<<<< HEAD
import json

from utils import (
    get_api_url, get_token, save_token, 
    get_categories, get_tasks, get_task, 
    get_solutions, get_solution, login, 
    create_task, create_solution, get_ai_chats, 
    get_ai_chat, send_ai_message
)

# Конфигурация страницы
st.set_page_config(
    page_title="Визуальная библиотека решений",
    page_icon="📚",
    layout="wide",
)

# Инициализация сессии
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False
if 'token' not in st.session_state:
    st.session_state.token = get_token()
    st.session_state.is_authenticated = st.session_state.token is not None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'tasks'
if 'selected_task' not in st.session_state:
    st.session_state.selected_task = None
if 'selected_solution' not in st.session_state:
    st.session_state.selected_solution = None
if 'selected_chat' not in st.session_state:
    st.session_state.selected_chat = None

# Функции навигации
def navigate_to(page):
    st.session_state.current_page = page
    # Сбросить выбранные элементы при смене страницы
    if page == 'tasks':
        st.session_state.selected_task = None
        st.session_state.selected_solution = None
    elif page == 'ai_assistant':
        st.session_state.selected_chat = None
    
    # Используем st.rerun() вместо st.experimental_rerun()
    st.rerun()





# Верхняя панель навигации
def render_navbar():
    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
    
    with col1:
        if st.button("📚 Задания", use_container_width=True):
            navigate_to('tasks')
    with col2:
        if st.button("💡 Решения", use_container_width=True):
            navigate_to('solutions')
    with col3:
        if st.button("🤖 ИИ-Ассистент", use_container_width=True):
            navigate_to('ai_assistant')
    with col4:
        if st.button("➕ Создать задание", use_container_width=True):
            navigate_to('create_task')
    with col5:
        if not st.session_state.is_authenticated:
            if st.button("🔑 Войти", use_container_width=True):
                navigate_to('login')
        else:
            if st.button("🚪 Выйти", use_container_width=True):
                st.session_state.is_authenticated = False
                st.session_state.token = None
                save_token(None)
                navigate_to('tasks')
    
    st.divider()

# Функция отрисовки страницы заданий
def render_tasks_page():
    st.title("📚 Библиотека заданий")
    
    # Фильтры и поиск
    col1, col2, col3 = st.columns([3, 2, 3])
    with col1:
        search_query = st.text_input("🔍 Поиск", "")
    with col2:
        categories = get_categories()
        # Преобразуем результат в список категорий
        categories_list = []
        if isinstance(categories, list):
            categories_list = categories
        elif isinstance(categories, dict) and "results" in categories:
            categories_list = categories["results"]
            
        category_options = ["Все категории"]
        # Безопасно добавляем имена категорий
        for cat in categories_list:
            if isinstance(cat, dict) and "name" in cat:
                category_options.append(cat["name"])
        
        selected_category = st.selectbox("Категория", category_options)
    with col3:
        difficulty_options = ["Все уровни", "Легкий", "Средний", "Сложный"]
        selected_difficulty = st.selectbox("Сложность", difficulty_options)
    
    # Загрузка заданий
    tasks = get_tasks(search_query)

# Детали задания
def render_task_detail():
    task_id = st.session_state.selected_task
    task = get_task(task_id)
    
    # Кнопка возврата
    if st.button("← Назад к заданиям"):
        navigate_to("tasks")
    
    st.title(task["title"])
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Категория:** {task['category_name']}")
        st.markdown(f"**Сложность:** {task['difficulty']}")
        st.markdown(f"**Автор:** {task['created_by']['username']}")
    with col2:
        if st.button("🤖 Сгенерировать решение", use_container_width=True):
            with st.spinner("Генерация решения..."):
                try:
                    api_url = get_api_url(f"tasks/{task_id}/generate_solution/")
                    response = requests.post(api_url, headers={"Authorization": f"Bearer {st.session_state.token}"})
                    if response.status_code == 200:
                        solution = response.json()
                        st.session_state.selected_solution = solution["id"]
                        navigate_to("solution_detail")
                    else:
                        st.error("Не удалось сгенерировать решение")
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")
    
    st.markdown("## Описание задания")
    st.write(task["description"])
    
    # Список решений
    st.markdown("## Решения")
    solutions = get_solutions(task_id=task_id)
    
    if not solutions:
        st.info("Решений пока нет")
    else:
        for solution in solutions:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    author_type = "🤖 ИИ" if solution["is_ai_generated"] else "👤 Пользователь"
                    st.markdown(f"**Автор:** {solution['author']['username']} ({author_type})")
                    st.markdown(f"**Добавлено:** {solution['created_at']}")
                with col2:
                    if st.button("Просмотреть", key=f"solution_{solution['id']}", use_container_width=True):
                        st.session_state.selected_solution = solution["id"]
                        navigate_to("solution_detail")

# Страница создания задания
def render_create_task():
    st.title("Создать новое задание")
    
    if not st.session_state.is_authenticated:
        st.warning("Необходимо войти в систему, чтобы создать задание")
        if st.button("Войти"):
            navigate_to("login")
        return
    
    with st.form("task_form"):
        title = st.text_input("Название задания")
        
        categories = get_categories()
        category_options = ["Все категории"] + [cat["name"] for cat in categories]
        category_dict = {cat["name"]: cat["id"] for cat in categories}
        selected_category = st.selectbox("Категория", category_options)
        
        difficulty = st.selectbox("Сложность", ["easy", "medium", "hard"])
        
        description = st.text_area("Описание задания", height=300)
        
        submitted = st.form_submit_button("Создать задание")
        
        if submitted:
            if not title or not description:
                st.error("Заполните все поля")
            else:
                with st.spinner("Создание задания..."):
                    try:
                        create_task(
                            title=title,
                            description=description,
                            difficulty=difficulty,
                            category=category_dict[selected_category]
                        )
                        st.success("Задание успешно создано!")
                        st.button("Вернуться к заданиям", on_click=lambda: navigate_to("tasks"))
                    except Exception as e:
                        st.error(f"Ошибка при создании задания: {str(e)}")

# Страница решения
def render_solution_detail():
    solution_id = st.session_state.selected_solution
    solution = get_solution(solution_id)
    
    # Кнопка возврата
    if st.button("← Назад к заданию"):
        navigate_to("task_detail")
    
    st.title(f"Решение: {solution['task_title']}")
    
    # Информация о решении
    author_type = "🤖 ИИ" if solution["is_ai_generated"] else "👤 Пользователь"
    st.markdown(f"**Автор:** {solution['author']['username']} ({author_type})")
    st.markdown(f"**Добавлено:** {solution['created_at']}")
    
    # Вкладки для кода и объяснения
    tab1, tab2, tab3 = st.tabs(["💻 Код", "📝 Объяснение", "🔍 Пошаговое воспроизведение"])
    
    with tab1:
        st.code(solution["code"], language="python")
    
    with tab2:
        st.write(solution["explanation"])
    
    with tab3:
        steps = solution.get("steps", [])
        if not steps:
            st.info("Пошаговое воспроизведение недоступно для этого решения")
        else:
            # Выбор шага
            step_number = st.slider("Шаг", 1, len(steps), 1)
            current_step = steps[step_number - 1]
            
            st.markdown(f"### Шаг {step_number} из {len(steps)}")
            st.write(current_step["explanation"])
            st.code(current_step["code_state"], language="python")

# Страница со всеми решениями
def render_solutions_page():
    st.title("💡 Все решения")
    
    # Фильтры и поиск
    col1, col2 = st.columns([1, 1])
    with col1:
        search_query = st.text_input("🔍 Поиск по названию задания", "")
    with col2:
        source_options = ["Все источники", "Только ИИ", "Только пользователи"]
        selected_source = st.selectbox("Источник", source_options)
    
    # Загрузка решений
    solutions = get_solutions()
    
    # Фильтрация решений
    if search_query:
        solutions = [sol for sol in solutions if search_query.lower() in sol["task_title"].lower()]
    if selected_source == "Только ИИ":
        solutions = [sol for sol in solutions if sol["is_ai_generated"]]
    elif selected_source == "Только пользователи":
        solutions = [sol for sol in solutions if not sol["is_ai_generated"]]
    
    # Отображение решений
    if not solutions:
        st.info("Решения не найдены")
    else:
        for solution in solutions:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(solution["task_title"])
                    author_type = "🤖 ИИ" if solution["is_ai_generated"] else "👤 Пользователь"
                    st.markdown(f"**Автор:** {solution['author']['username']} ({author_type})")
                    st.markdown(f"**Добавлено:** {solution['created_at']}")
                with col2:
                    if st.button("Просмотреть", key=f"sol_{solution['id']}", use_container_width=True):
                        st.session_state.selected_solution = solution["id"]
                        navigate_to("solution_detail")

# Страница ИИ-ассистента
def render_ai_assistant():
    st.title("🤖 ИИ-Ассистент", anchor=False)
    
    if not st.session_state.is_authenticated:
        st.warning("Необходимо войти в систему, чтобы использовать ИИ-ассистента")
        if st.button("Войти", key="login_ai_assistant"):
            navigate_to("login")
        return
    
    # Создаем два столбца для лучшей компоновки
    chat_col, sidebar_col = st.columns([3, 1])
    
    # Боковая панель с чатами
    with sidebar_col:
        st.header("Ваши чаты")
        
        # Создание нового чата
        new_chat_title = st.text_input("Название нового чата", key="new_chat_title_input")
        if st.button("Создать чат", key="create_chat_button"):
            if new_chat_title:
                try:
                    api_url = get_api_url("ai-chats/")
                    print(f"API URL для создания чата: {api_url}")
                    
                    headers = {"Authorization": f"Token {st.session_state.token}"}
                    print(f"Заголовки: {headers}")
                    
                    payload = {"title": new_chat_title}
                    print(f"Отправляемые данные: {payload}")
                    
                    response = requests.post(
                        api_url, 
                        json=payload,
                        headers=headers
                    )
                    
                    print(f"Статус ответа: {response.status_code}")
                    print(f"Ответ сервера: {response.text}")
                    
                    if response.status_code == 201:
                        chat = response.json()
                        st.session_state.selected_chat = chat["id"]
                        st.experimental_rerun()
                    else:
                        st.error(f"Не удалось создать чат: {response.status_code} - {response.text}")
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    print(f"Подробности исключения:\n{error_details}")
                    st.error(f"Не удалось создать чат: {str(e)}")
        
        st.divider()
        
        # Список существующих чатов
        chats = get_ai_chats()
        
        # Добавьте проверку типа данных
        print(f"Тип переменной chats: {type(chats)}")
        print(f"Содержимое chats: {chats}")
        
        # Список для прошедших проверку чатов
        valid_chats = []
        
        # Проверяем каждый элемент
        if isinstance(chats, list):
            for chat in chats:
                if isinstance(chat, dict) and "id" in chat and "title" in chat:
                    valid_chats.append(chat)
        elif isinstance(chats, dict) and "results" in chats:
            for chat in chats["results"]:
                if isinstance(chat, dict) and "id" in chat and "title" in chat:
                    valid_chats.append(chat)
        
        # Используем только правильно структурированные чаты
        for i, chat in enumerate(valid_chats):
            if st.button(chat["title"], key=f"chat_{chat['id']}_{i}", use_container_width=True):
                st.session_state.selected_chat = chat["id"]
                st.experimental_rerun()
    
    # Основная область чата
    with chat_col:
        if st.session_state.selected_chat:
            chat = get_ai_chat(st.session_state.selected_chat)
            
            if chat and "title" in chat:
                st.subheader(chat["title"])
                
                # Создаем контейнер для истории сообщений
                chat_container = st.container()
                
                # Отображение сообщений
                messages = []
                if "messages" in chat and isinstance(chat["messages"], list):
                    messages = chat["messages"]
                
                with chat_container:
                    for message in messages:
                        if isinstance(message, dict) and "role" in message and "content" in message:
                            if message["role"] == "user":
                                with st.chat_message("user"):
                                    st.write(message["content"])
                            elif message["role"] == "assistant":
                                with st.chat_message("assistant"):
                                    st.write(message["content"])
                            # Системные сообщения не отображаем
                
                # Поле для ввода сообщения
                user_message = st.chat_input("Введите сообщение...")
                if user_message:
                    with st.chat_message("user"):
                        st.write(user_message)
                    
                    with st.spinner("ИИ думает..."):
                        try:
                            response = send_ai_message(st.session_state.selected_chat, user_message)
                            
                            # Проверяем тип и структуру ответа
                            if isinstance(response, list):
                                for msg in response:
                                    if isinstance(msg, dict) and msg.get("role") == "assistant":
                                        with st.chat_message("assistant"):
                                            st.write(msg.get("content", "Пустой ответ"))
                            elif isinstance(response, str):
                                with st.chat_message("assistant"):
                                    st.write(response)
                            elif isinstance(response, dict):
                                # Прямой ответ в виде словаря
                                if "content" in response:
                                    with st.chat_message("assistant"):
                                        st.write(response["content"])
                                # Словарь из успешной операции API
                                elif "response" in response:
                                    with st.chat_message("assistant"):
                                        st.write(response["response"])
                            else:
                                st.error("Получен неизвестный формат ответа")
                        except Exception as e:
                            st.error(f"Ошибка при отправке сообщения: {str(e)}")
            else:
                st.error("Не удалось загрузить чат")
        else:
            st.info("Выберите чат или создайте новый")
            
            # Добавляем информацию о возможностях ИИ-ассистента
            st.markdown("""
            ### Что умеет ИИ-ассистент:
            - Помогать с решением задач
            - Объяснять алгоритмы и код
            - Отвечать на вопросы по программированию
            - Генерировать решения для заданий
            """)

def main():
    st.title("Визуальная библиотека решений")
    st.write("Это тестовая страница")

def main():
    try:
        render_navbar()
        
        # Отображение нужной страницы
        if st.session_state.current_page == 'tasks':
            render_tasks_page()
        elif st.session_state.current_page == 'ai_assistant':
            render_ai_assistant()
        # и т.д.
    except Exception as e:
        st.error(f"Произошла ошибка: {str(e)}")
        import traceback
        st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
=======
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
>>>>>>> 86c897f86fa626be424a70e192037cedb663dda8
