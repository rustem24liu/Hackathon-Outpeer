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
    st.title("🤖 ИИ-Ассистент")
    
    if not st.session_state.is_authenticated:
        st.warning("Необходимо войти в систему, чтобы использовать ИИ-ассистента")
        if st.button("Войти", key="login_ai_assistant"):  # Добавлен уникальный ключ
            navigate_to("login")
        return
    
    # Боковая панель с чатами
    with st.sidebar:
        st.header("Ваши чаты")
        
        # Создание нового чата
        new_chat_title = st.text_input("Название нового чата")  # Определяем переменную здесь
        if st.button("Создать чат", key="create_chat_button"):  # Добавлен уникальный ключ
            if new_chat_title:
                try:
                    api_url = get_api_url("ai-chats/")
                    print(f"API URL для создания чата: {api_url}")
                    
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
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
                        st.error("Не удалось создать чат")
                        print(f"Подробности ошибки: {response.text}")
                except Exception as e:
                    st.error("Не удалось создать чат")
                    print(f"Исключение: {str(e)}")
        
        st.divider()
        
        # Список существующих чатов
        chats = get_ai_chats()
        for chat in chats:
            if st.button(chat["title"], key=f"chat_{chat['id']}", use_container_width=True):  # Добавлен уникальный ключ
                st.session_state.selected_chat = chat["id"]
                st.experimental_rerun()
# Страница входа
def render_login():
    st.title("🔑 Вход в систему")
    
    if st.session_state.is_authenticated:
        st.success("Вы уже вошли в систему")
        if st.button("Перейти к заданиям"):
            navigate_to("tasks")
        return
    
    with st.form("login_form"):
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type="password")
        
        submitted = st.form_submit_button("Войти")
        
        if submitted:
            if not username or not password:
                st.error("Введите имя пользователя и пароль")
            else:
                with st.spinner("Выполняется вход..."):
                    token = login(username, password)
                    if token:
                        st.session_state.token = token
                        st.session_state.is_authenticated = True
                        save_token(token)
                        st.success("Вход выполнен успешно!")
                        st.session_state.current_page = "tasks"  # Изменяем страницу сразу
                    else:
                        st.error("Неверное имя пользователя или пароль")

# Основная функция приложения
def main():
    render_navbar()
    
    # Отображение нужной страницы в зависимости от состояния
    if st.session_state.current_page == 'tasks':
        render_tasks_page()
    elif st.session_state.current_page == 'task_detail':
        render_task_detail()
    elif st.session_state.current_page == 'create_task':
        render_create_task()
    elif st.session_state.current_page == 'solutions':
        render_solutions_page()
    elif st.session_state.current_page == 'solution_detail':
        render_solution_detail()
    elif st.session_state.current_page == 'ai_assistant':
        render_ai_assistant()
    elif st.session_state.current_page == 'login':
        render_login()


# Находим этот блок кода
if st.button("Создать чат"):
    if new_chat_title:
        try:
            api_url = get_api_url("ai-chats/")
            print(f"API URL для создания чата: {api_url}")  # Отладочный вывод
            
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            print(f"Заголовки: {headers}")  # Отладка заголовков
            
            payload = {"title": new_chat_title}
            print(f"Отправляемые данные: {payload}")  # Отладка данных
            
            response = requests.post(
                api_url, 
                json=payload,
                headers=headers
            )
            
            print(f"Статус ответа: {response.status_code}")  # Отладка статуса
            print(f"Ответ сервера: {response.text}")  # Отладка ответа
            
            if response.status_code == 201:
                chat = response.json()
                st.session_state.selected_chat = chat["id"]
                st.experimental_rerun()
            else:
                st.error("Не удалось создать чат")
                print(f"Подробности ошибки: {response.text}")  # Детали ошибки
        except Exception as e:
            st.error("Не удалось создать чат")
            print(f"Исключение: {str(e)}")  # Печать исключения


if __name__ == "__main__":
    main()