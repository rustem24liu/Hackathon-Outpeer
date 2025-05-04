import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import os
from utils import (
    highlight_code, 
    get_highlighting_css, 
    get_language_from_extension,
    read_file, 
    format_timestamp,
    parse_solution_steps,
    get_display_name,
    get_code_explanation_from_ai
)
from data_manager import (
    get_solution_by_id,
    get_user_by_id,
    get_comments_for_solution,
    get_solution_average_rating,
    get_solution_rating_count,
    add_comment,
    add_or_update_rating,
    increment_solution_views,
    get_all_tags
)
import openai


from authentication import require_auth


# def analyze_code_with_gpt(code: str):
#     """Отправляет код на анализ в ChatGPT"""
#     openai.api_key = key
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "Ты помощник-программист. Проанализируй код, найди ошибки, предложи улучшения и кратко опиши, что делает код."},
#                 {"role": "user", "content": f"Вот код:\n\n{code}"}
#             ],
#             temperature=0.5,
#             max_tokens=800
#         )
#         return response['choices'][0]['message']['content']
#     except:
#         return f"❌ Ошибка при обращении к OpenAI API"


# Apply syntax highlighting CSS
def apply_highlighting_css():
    """Apply syntax highlighting CSS"""
    css = get_highlighting_css()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Display a solution card in the solution list
def solution_card(solution):
    """Display a solution card in the solution list"""
    user = get_user_by_id(solution["user_id"])
    username = user["username"] if user else "Unknown User"
    avg_rating = get_solution_average_rating(solution["id"])
    rating_count = get_solution_rating_count(solution["id"])
    
    with st.container():
        col1, col2, col3 = st.columns([2, 3, 1])
        
        with col1:
            st.subheader(solution["title"])
            st.caption(f"By {username} • {format_timestamp(solution['created_at'])}")
        
        with col2:
            st.write(solution["description"][:100] + "..." if len(solution["description"]) > 100 else solution["description"])
            
            # Show tags
            if solution.get("tags"):
                for tag in solution["tags"]:
                    st.markdown(f"<span style='background-color:#E6E6E6;padding:2px 5px;border-radius:5px;margin-right:5px;font-size:0.8em'>{tag}</span>", unsafe_allow_html=True)
        
        with col3:
            st.write(f"⭐ {avg_rating:.1f} ({rating_count})")
            st.write(f"👁️ {solution.get('views', 0)}")
            if st.button("View", key=f"view_{solution['id']}"):
                st.session_state.page = "solution_detail"
                st.session_state.solution_id = solution["id"]
                st.rerun()
        
        st.markdown("---")

# Display solution details page
def solution_detail_page(solution_id):
    """Display solution details page"""
    # Increment view count
    increment_solution_views(solution_id)
    
    solution = get_solution_by_id(solution_id)
    if not solution:
        st.error("Solution not found.")
        return
    
    user = get_user_by_id(solution["user_id"])
    username = user["username"] if user else "Unknown User"
    
    # Apply syntax highlighting CSS
    apply_highlighting_css()
    
    # Solution header
    st.title(solution["title"])
    st.markdown(f"By {username} • {format_timestamp(solution['created_at'])}")
    
    # Rating display and control
    avg_rating = get_solution_average_rating(solution_id)
    rating_count = get_solution_rating_count(solution_id)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write(f"⭐ {avg_rating:.1f} ({rating_count} ratings)")
    
    with col2:
        if st.session_state.is_authenticated:
            user_rating = st.slider("Оценить это решение", 1, 5, 3, key=f"rating_{solution_id}")
            if st.button("Отправить оценку"):
                add_or_update_rating(solution_id, st.session_state.user_id, user_rating)
                st.success("Оценка отправлена!")
                st.rerun()
    
    # Tags
    if solution.get("tags"):
        st.write("Теги:")
        cols = st.columns(5)
        for i, tag in enumerate(solution["tags"]):
            with cols[i % 5]:
                st.markdown(f"<span style='background-color:#E6E6E6;padding:2px 5px;border-radius:5px;margin-right:5px;font-size:0.8em'>{tag}</span>", unsafe_allow_html=True)
    
    # Description
    st.markdown("## Описание")
    st.write(solution["description"])
    
    # Solution steps
    st.markdown("## Решение")
    
    try:
        file_path = solution["file_path"]
        display_name = get_display_name(file_path)
        language = get_language_from_extension(file_path)
        
        st.write(f"Файл: {display_name}")
        
        # Parse solution into steps
        steps = parse_solution_steps(file_path)
        
        # AI Assistant button
        st.markdown("### ИИ Ассистент")
        if st.button("Объяснить код с помощью ИИ", key=f"ai_explain_{solution_id}"):
            with st.spinner("ИИ анализирует код..."):
                full_content = read_file(file_path)
                explanation = get_code_explanation_from_ai(full_content, language)
                st.session_state[f"ai_explanation_{solution_id}"] = explanation
        
        # Display AI explanation if available
        if f"ai_explanation_{solution_id}" in st.session_state:
            with st.expander("Объяснение кода от ИИ", expanded=True):
                # Make the AI explanation look better
                explanation_text = st.session_state[f"ai_explanation_{solution_id}"]
                
                # Split explanation by sections if they exist (often contains headers with ###)
                sections = []
                current_section = []
                
                for line in explanation_text.split("\n"):
                    if line.startswith("###") or line.startswith("##"):
                        if current_section:
                            sections.append("\n".join(current_section))
                            current_section = []
                    current_section.append(line)
                
                if current_section:
                    sections.append("\n".join(current_section))
                
                # If there are clear sections, display them in a more structured way
                if len(sections) > 1:
                    for section in sections:
                        st.markdown(section)
                        st.markdown("---")
                else:
                    # Otherwise just display the full explanation
                    st.markdown(explanation_text)
        
        if steps:
            # Step navigation
            st.markdown("### Пошаговое решение")
            
            # Initialize step index in session state if not present
            if f"step_index_{solution_id}" not in st.session_state:
                st.session_state[f"step_index_{solution_id}"] = 0
            
            # Step navigation controls
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                if st.button("Предыдущий шаг", key=f"prev_{solution_id}", disabled=st.session_state[f"step_index_{solution_id}"] == 0):
                    st.session_state[f"step_index_{solution_id}"] -= 1
                    st.rerun()
            
            with col2:
                step_index = st.session_state[f"step_index_{solution_id}"]
                st.progress((step_index + 1) / len(steps))
                st.caption(f"Шаг {step_index + 1} из {len(steps)}")
            
            with col3:
                if st.button("Следующий шаг", key=f"next_{solution_id}", disabled=st.session_state[f"step_index_{solution_id}"] == len(steps) - 1):
                    st.session_state[f"step_index_{solution_id}"] += 1
                    st.rerun()
            
            # Display current step with proper structure like Google Colab
            step_index = st.session_state[f"step_index_{solution_id}"]
            step_content = steps[step_index]
            
            # Split into code and comments if possible
            code_lines = step_content.split('\n')
            current_block = []
            current_type = None  # 'comment' or 'code'
            content_blocks = []
            
            for line in code_lines:
                line_stripped = line.strip()
                # Determine if this line is a comment
                is_comment = False
                if language == 'python':
                    is_comment = line_stripped.startswith('#') or line_stripped.startswith('"""') or line_stripped.startswith("'''")
                elif language in ['javascript', 'java', 'cpp', 'c']:
                    is_comment = line_stripped.startswith('//') or line_stripped.startswith('/*') or line_stripped.startswith('*')
                
                # If we're switching block types or at the first line
                if (is_comment and current_type != 'comment') or (not is_comment and current_type != 'code') or current_type is None:
                    # Save the previous block if it exists
                    if current_block:
                        content_blocks.append({
                            'type': current_type,
                            'content': '\n'.join(current_block)
                        })
                        current_block = []
                    
                    # Set the new type
                    current_type = 'comment' if is_comment else 'code'
                
                # Add the line to the current block
                current_block.append(line)
            
            # Add the last block
            if current_block:
                content_blocks.append({
                    'type': current_type,
                    'content': '\n'.join(current_block)
                })
            
            # Display blocks in a Colab-like style
            for i, block in enumerate(content_blocks):
                if block['type'] == 'comment':
                    # Display comments as markdown text with light styling
                    # Escape triple quotes in the content to prevent syntax errors
                    clean_content = block['content'].replace('#', '')
                    clean_content = clean_content.replace('"""', '\\"\\"\\"').replace("'''", "\\'\\'\\'")
                    clean_content = clean_content.strip()
                    
                    st.markdown(f"""
                    <div style="background-color: #f9f9f9; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                        {clean_content}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Display code with syntax highlighting in a code block
                    st.markdown(f"""
                    <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                        {highlight_code(block['content'], language)}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Option to view full solution
            if st.checkbox("Просмотреть полное решение", key=f"full_{solution_id}"):
                full_content = read_file(file_path)
                st.markdown("### Полное решение")
                
                # Split into code and comments blocks
                code_lines = full_content.split('\n')
                current_block = []
                current_type = None  # 'comment' or 'code'
                content_blocks = []
                
                for line in code_lines:
                    line_stripped = line.strip()
                    # Determine if this line is a comment
                    is_comment = False
                    if language == 'python':
                        is_comment = line_stripped.startswith('#') or line_stripped.startswith('"""') or line_stripped.startswith("'''")
                    elif language in ['javascript', 'java', 'cpp', 'c']:
                        is_comment = line_stripped.startswith('//') or line_stripped.startswith('/*') or line_stripped.startswith('*')
                    
                    # If we're switching block types or at the first line
                    if (is_comment and current_type != 'comment') or (not is_comment and current_type != 'code') or current_type is None:
                        # Save the previous block if it exists
                        if current_block:
                            content_blocks.append({
                                'type': current_type,
                                'content': '\n'.join(current_block)
                            })
                            current_block = []
                        
                        # Set the new type
                        current_type = 'comment' if is_comment else 'code'
                    
                    # Add the line to the current block
                    current_block.append(line)
                
                # Add the last block
                if current_block:
                    content_blocks.append({
                        'type': current_type,
                        'content': '\n'.join(current_block)
                    })
                
                # Display blocks in a Colab-like style
                for i, block in enumerate(content_blocks):
                    if block['type'] == 'comment':
                        # Display comments as markdown text with light styling
                        # Escape triple quotes in the content to prevent syntax errors
                        clean_content = block['content'].replace('#', '')
                        # Simple clean up
                        clean_content = clean_content.strip()
                        
                        if clean_content:  # Only display if there's actual content after removing comment symbols
                            # Create HTML without f-strings for comment blocks
                            html = '<div style="background-color: #f9f9f9; padding: 10px; border-radius: 5px; margin-bottom: 10px;">'
                            html += clean_content
                            html += '</div>'
                            
                            st.markdown(html, unsafe_allow_html=True)
                    else:
                        # Display code with syntax highlighting in a code block
                        st.markdown(f"""
                        <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                            {highlight_code(block['content'], language)}
                        </div>
                        """, unsafe_allow_html=True)
        else:
            # If steps couldn't be parsed, structure the full content similar to Colab
            full_content = read_file(file_path)
            
            # Split into code and comments blocks
            code_lines = full_content.split('\n')
            current_block = []
            current_type = None  # 'comment' or 'code'
            content_blocks = []
            
            for line in code_lines:
                line_stripped = line.strip()
                # Determine if this line is a comment
                is_comment = False
                if language == 'python':
                    is_comment = line_stripped.startswith('#') or line_stripped.startswith('"""') or line_stripped.startswith("'''")
                elif language in ['javascript', 'java', 'cpp', 'c']:
                    is_comment = line_stripped.startswith('//') or line_stripped.startswith('/*') or line_stripped.startswith('*')
                
                # If we're switching block types or at the first line
                if (is_comment and current_type != 'comment') or (not is_comment and current_type != 'code') or current_type is None:
                    # Save the previous block if it exists
                    if current_block:
                        content_blocks.append({
                            'type': current_type,
                            'content': '\n'.join(current_block)
                        })
                        current_block = []
                    
                    # Set the new type
                    current_type = 'comment' if is_comment else 'code'
                
                # Add the line to the current block
                current_block.append(line)
            
            # Add the last block
            if current_block:
                content_blocks.append({
                    'type': current_type,
                    'content': '\n'.join(current_block)
                })
            
            # Display blocks in a Colab-like style
            for i, block in enumerate(content_blocks):
                if block['type'] == 'comment':
                    # Display comments as markdown text with light styling
                    # Simple clean up
                    comment_content = block['content'].replace('#', '').strip()
                    
                    if comment_content:  # Only display if there's actual content after removing comment symbols
                        # Create HTML without f-strings for comment blocks
                        html = '<div style="background-color: #f9f9f9; padding: 10px; border-radius: 5px; margin-bottom: 10px;">'
                        html += comment_content
                        html += '</div>'
                        
                        st.markdown(html, unsafe_allow_html=True)
                else:
                    # Display code with syntax highlighting in a code block
                    st.markdown(f"""
                    <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                        {highlight_code(block['content'], language)}
                    </div>
                    """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Ошибка отображения решения: {str(e)}")
    
    # Comments section
    st.markdown("## Комментарии")
    comments = get_comments_for_solution(solution_id)
    
    if comments:
        for comment in sorted(comments, key=lambda x: x["created_at"], reverse=True):
            comment_user = get_user_by_id(comment["user_id"])
            comment_username = comment_user["username"] if comment_user else "Unknown User"
            
            with st.container():
                st.markdown(f"**{comment_username}** - {format_timestamp(comment['created_at'])}")
                st.write(comment["content"])
                st.markdown("---")
    else:
        st.write("Пока нет комментариев.")
    
    # Add comment form
    if st.session_state.is_authenticated:
        with st.form(key=f"comment_form_{solution_id}"):
            comment_text = st.text_area("Добавить комментарий", key=f"comment_{solution_id}")
            submit_comment = st.form_submit_button("Отправить комментарий")
            
            if submit_comment and comment_text:
                add_comment(solution_id, st.session_state.user_id, comment_text)
                st.success("Комментарий отправлен!")
                st.rerun()
    else:
        st.info("Пожалуйста, войдите в систему, чтобы добавить комментарии.")
    
    # Back button
    if st.button("Вернуться к списку решений"):
        st.session_state.page = "solution_list"
        st.rerun()

# Display upload solution form
def upload_solution_form():
    """Display upload solution form"""
    import streamlit as st
    
    if not require_auth():
        return
    
    st.title("Загрузка решения")
    
    # Instructions
    with st.expander("Как загрузить своё решение?", expanded=True):
        st.markdown("""
        ### Как загрузить своё решение
        
        1. Укажите название решения, которое кратко описывает задачу или алгоритм
        2. Добавьте подробное описание: что решает алгоритм, как он работает, для чего используется
        3. Добавьте ключевые теги через запятую (например: "сортировка, массивы, python")
        4. Загрузите файл с вашим решением
        5. Для лучшей визуализации по шагам, добавьте комментарии в коде начинающиеся с "# Step" или "// Step"
        
        Ваше решение будет доступно другим студентам для изучения и комментирования.
        """)
    
    # Initialize session state for code blocks
    if 'code_blocks' not in st.session_state:
        st.session_state.code_blocks = [{'type': 'code', 'content': '# Введите свой код здесь\n\ndef hello_world():\n    print("Привет, мир!")\n    \n    # Вычисляем сумму чисел\n    total = 0\n    for i in range(10):\n        total += i\n    \n    return total'}]
    
    # Form for basic information
    with st.form("upload_solution_form"):
        title = st.text_input("Название решения")
        description = st.text_area("Описание", 
                                 placeholder="Опишите, что делает ваше решение, какие алгоритмы используются, для какой задачи оно предназначено и т.д.")
        
        # Tags input
        tags_input = st.text_input("Теги (через запятую)", 
                                  placeholder="Например: линейная регрессия, классификация, python")
        
        # Choose upload method
        upload_method = st.radio("Способ добавления решения", 
                               ["Загрузить файл", "Создать структурированное решение"],
                               index=1)
        
        if upload_method == "Загрузить файл":
            # File upload
            uploaded_file = st.file_uploader("Загрузить файл с решением", 
                                          type=["py", "js", "html", "css", "java", "cpp", "c", "cs", "txt"])
            #Мой код
            # if uploaded_file and st.button("🔍 Проверить решение через ChatGPT"):
            #     code = uploaded_file.read().decode("utf-8")
            #     with st.spinner("Анализируем решение..."):
            #         analysis = analyze_code_with_gpt(code)
            #     st.markdown("### 💡 Результаты анализа")
            #     st.write(analysis)
            # Мой код

        else:
            uploaded_file = None
            # This is just a placeholder for the form
            st.write("После нажатия кнопки вы сможете структурировать своё решение")
        
        submit_button = st.form_submit_button("Продолжить")
        
        if submit_button:
            if not title or not description or (upload_method == "Загрузить файл" and not uploaded_file):
                st.error("Пожалуйста, заполните все поля.")
            else:
                if upload_method == "Загрузить файл":
                    from data_manager import add_solution
                    
                    # Process tags
                    tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
                    
                    solution_id = add_solution(
                        title=title,
                        description=description,
                        uploaded_file=uploaded_file,
                        user_id=st.session_state.user_id,
                        tags=tags
                    )
                    
                    if solution_id:
                        st.success("Решение успешно загружено!")
                        st.session_state.page = "solution_detail"
                        st.session_state.solution_id = solution_id
                        st.rerun()
                    else:
                        st.error("Не удалось загрузить решение.")
                else:
                    # Save form data to session state
                    st.session_state.form_title = title
                    st.session_state.form_description = description
                    st.session_state.form_tags = tags_input
                    # Show code block editor
                    st.session_state.show_block_editor = True
                    st.rerun()

    # Show block editor if needed
    if st.session_state.get('show_block_editor', False):
        st.subheader("Структурированное решение")
        st.markdown("""
        Создайте структурированное решение, чередуя блоки кода и текстовые описания.
        Такой формат похож на Jupyter Notebook или Google Colab.
        """)
        
        # Display existing blocks
        for i, block in enumerate(st.session_state.code_blocks):
            col1, col2 = st.columns([5, 1])
            
            with col1:
                if block['type'] == 'code':
                    # Используем st.code для отображения кода с сохранением форматирования
                    # Важно: удаляем только пробелы в начале и конце, сохраняем все переносы строк и отступы внутри кода
                    #st.code(block['content'].strip(), language="python")
                    st.markdown('```python\n' + block['content'] + '\n```', unsafe_allow_html=True)
                else:
                    # Create HTML without f-strings for text blocks
                    html_code = '<div style="background-color: #f9f9f9; padding: 10px; border-radius: 5px; margin-bottom: 10px;">'
                    html_code += block['content']
                    html_code += '</div>'
                    
                    st.markdown(html_code, unsafe_allow_html=True)
            
            with col2:
                if st.button("Редактировать", key=f"edit_{i}"):
                    st.session_state.editing_block = i
                    st.rerun()
                
                if len(st.session_state.code_blocks) > 1 and st.button("Удалить", key=f"delete_{i}"):
                    st.session_state.code_blocks.pop(i)
                    st.rerun()
        
        # Editor for selected block
        if 'editing_block' in st.session_state:
            i = st.session_state.editing_block
            block = st.session_state.code_blocks[i]
            
            st.markdown("### Редактирование блока")
            block_type = st.radio("Тип блока", ["Код", "Описание"], 
                                index=0 if block['type'] == 'code' else 1, 
                                key=f"type_{i}")
            
            if block_type == "Код":
                new_content = st.text_area("Код", value=block['content'], height=200, key=f"content_{i}")
                st.session_state.code_blocks[i] = {'type': 'code', 'content': new_content}
            else:
                new_content = st.text_area("Описание", value=block['content'], height=200, key=f"content_{i}")
                st.session_state.code_blocks[i] = {'type': 'text', 'content': new_content}
            
            if st.button("Готово", key=f"done_{i}"):
                del st.session_state.editing_block
                st.rerun()
        
        # Add new block buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("+ Добавить блок кода"):
                st.session_state.code_blocks.append({'type': 'code', 'content': '# Новый блок кода'})
                st.rerun()
        
        with col2:
            if st.button("+ Добавить описание"):
                st.session_state.code_blocks.append({'type': 'text', 'content': 'Введите текстовое описание здесь'})
                st.rerun()
        # Мой код
        # if st.button("🔍 Проверить решение через ChatGPT"):
        #     code_content = ""
        #     for block in st.session_state.code_blocks:
        #         if block['type'] == 'code':
        #             code_content += block['content'].rstrip() + "\n\n"
        #         else:
        #             lines = block['content'].strip().split("\n")
        #             for line in lines:
        #                 code_content += "# " + line + "\n"
        #             code_content += "\n"
        #
        #     with st.spinner("Анализируем решение..."):
        #         analysis = analyze_code_with_gpt(code_content)
        #
        #     st.markdown("### 💡 Результаты анализа")
        #     st.write(analysis)
            #Мой код
        
        # Submit button for structured solution
        if st.button("Сохранить и загрузить решение", type="primary"):
            # Generate code file from blocks with proper formatting
            code_content = ""
            for block in st.session_state.code_blocks:
                if block['type'] == 'code':
                    # Сохраняем код как есть с правильными отступами
                    code_content += block['content'].rstrip() + "\n\n"
                else:
                    # Добавляем комментарии с отступом в одну строку для каждой строки текста
                    lines = block['content'].strip().split("\n")
                    for line in lines:
                        code_content += "# " + line + "\n"
                    code_content += "\n"
            
            # Create temporary file
            import io
            import tempfile
            import os
            
            # Create temporary file with the generated code
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
                f.write(code_content.encode('utf-8'))
                temp_file_name = f.name
            
            # Prepare for upload
            from data_manager import add_solution
            import streamlit as st
            
            # Read the temp file
            with open(temp_file_name, 'rb') as f:
                file_content = f.read()
            
            # Create file-like object
            file_obj = io.BytesIO(file_content)
            file_obj.name = "solution.py"
            
            # Process tags
            tags = [tag.strip() for tag in st.session_state.form_tags.split(",")] if st.session_state.form_tags else []
            
            # Add solution
            solution_id = add_solution(
                title=st.session_state.form_title,
                description=st.session_state.form_description,
                uploaded_file=file_obj,
                user_id=st.session_state.user_id,
                tags=tags
            )
            
            # Clean up
            os.unlink(temp_file_name)
            
            if solution_id:
                # Reset session state
                if 'code_blocks' in st.session_state:
                    del st.session_state.code_blocks
                if 'show_block_editor' in st.session_state:
                    del st.session_state.show_block_editor
                if 'form_title' in st.session_state:
                    del st.session_state.form_title
                if 'form_description' in st.session_state:
                    del st.session_state.form_description
                if 'form_tags' in st.session_state:
                    del st.session_state.form_tags
                
                st.success("Решение успешно загружено!")
                st.session_state.page = "solution_detail"
                st.session_state.solution_id = solution_id
                st.rerun()
            else:
                st.error("Не удалось загрузить решение.")

# Display solution list with filtering
def solution_list_page():
    """Display solution list with filtering"""
    st.title("Библиотека решений")
    
    # Filters
    with st.expander("Фильтры и поиск"):
        col1, col2 = st.columns(2)
        
        with col1:

            tags = ["Все"] + get_all_tags()
            selected_tag = st.selectbox("Фильтр по тегу", tags, index=0)
        
        with col2:
            sort_options = ["Новые", "Старые", "Высокий рейтинг", "Популярные"]
            sort_by = st.selectbox("Сортировка", sort_options)
        
        # Search
        search_query = st.text_input("Поиск решений", "", placeholder="Введите слова для поиска")
    
    # Get solutions based on filters
    from data_manager import get_all_solutions, get_solutions_by_tag, search_solutions
    
    if search_query:
        solutions = search_solutions(search_query)
    elif selected_tag != "Все":
        solutions = get_solutions_by_tag(selected_tag)
    else:
        solutions = get_all_solutions()
    
    # Sort solutions
    if sort_by == "Новые":
        solutions = sorted(solutions, key=lambda x: x["created_at"], reverse=True)
    elif sort_by == "Старые":
        solutions = sorted(solutions, key=lambda x: x["created_at"])
    elif sort_by == "Высокий рейтинг":
        solutions = sorted(solutions, key=lambda x: get_solution_average_rating(x["id"]), reverse=True)
    elif sort_by == "Популярные":
        solutions = sorted(solutions, key=lambda x: x.get("views", 0), reverse=True)
    
    # Display solutions
    if solutions:
        st.write(f"Найдено решений: {len(solutions)}")
        for solution in solutions:
            solution_card(solution)
    else:
        st.write("Решения не найдены.")
    
    # Upload button
    if st.session_state.is_authenticated:
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Загрузить своё решение", type="primary"):
                st.session_state.page = "upload_solution"
                st.rerun()
    else:
        st.info("Пожалуйста, выполните вход, чтобы загружать свои решения.")

# Dashboard page
def dashboard_page():
    """Display dashboard with statistics"""
    if not require_auth():
        return
    
    st.title("Моя панель управления")
    
    # Get user's solutions
    from data_manager import get_solutions_by_user
    user_solutions = get_solutions_by_user(st.session_state.user_id)
    
    # Stats summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Всего решений", len(user_solutions))
    
    with col2:
        total_views = sum(solution.get("views", 0) for solution in user_solutions)
        st.metric("Всего просмотров", total_views)
    
    with col3:
        from data_manager import get_all_ratings
        ratings = get_all_ratings()
        user_solution_ids = [solution["id"] for solution in user_solutions]
        solution_ratings = [r for r in ratings if r["solution_id"] in user_solution_ids]
        
        avg_rating = 0
        if solution_ratings:
            avg_rating = sum(r["rating"] for r in solution_ratings) / len(solution_ratings)
        
        st.metric("Средний рейтинг", f"{avg_rating:.1f}")
    
    # Visualizations
    if user_solutions:
        st.subheader("Статистика просмотров")
        
        # Prepare data for chart
        solution_titles = [s["title"] if len(s["title"]) < 20 else s["title"][:17] + "..." for s in user_solutions]
        solution_views = [s.get("views", 0) for s in user_solutions]
        
        # Create a DataFrame
        data = pd.DataFrame({
            "Решение": solution_titles,
            "Просмотры": solution_views
        })
        
        # Sort by views
        data = data.sort_values("Просмотры", ascending=False)
        
        # Create bar chart
        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(data["Решение"], data["Просмотры"], color="skyblue")
        
        # Add labels and title
        ax.set_xlabel("Решение")
        ax.set_ylabel("Просмотры")
        ax.set_title("Просмотры по решениям")
        
        # Rotate x-axis labels
        plt.xticks(rotation=45, ha="right")
        
        # Add values on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    str(int(height)), ha="center", va="bottom")
        
        plt.tight_layout()
        st.pyplot(fig)
    
    # User's solutions
    st.subheader("Мои решения")
    
    if user_solutions:
        for solution in sorted(user_solutions, key=lambda x: x["created_at"], reverse=True):
            solution_card(solution)
    else:
        st.write("Вы еще не загрузили ни одного решения.")
        
        if st.button("Загрузить своё первое решение", type="primary"):
            st.session_state.page = "upload_solution"
            st.rerun()
