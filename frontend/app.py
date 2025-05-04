import streamlit as st
import requests
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