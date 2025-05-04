import streamlit as st
import os
from authentication import initialize_session_state, auth_page, logout_user
from components import (
    solution_list_page,
    solution_detail_page,
    upload_solution_form,
    dashboard_page
)

# Set page configuration
st.set_page_config(
    page_title="Visual Solution Library",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
initialize_session_state()

# Initialize page if not already set
if 'page' not in st.session_state:
    st.session_state.page = 'solution_list'

# Sidebar navigation
with st.sidebar:
    st.title("Библиотека решений")
    st.markdown("---")
    
    # Navigation links
    if st.button("📚 Библиотека решений"):
        st.session_state.page = 'solution_list'
        st.rerun()
    
    if st.session_state.is_authenticated:
        if st.button("📊 Моя панель"):
            st.session_state.page = 'dashboard'
            st.rerun()
        
        if st.button("📤 Загрузить решение"):
            st.session_state.page = 'upload_solution'
            st.rerun()
    
    st.markdown("---")
    
    # Authentication section
    if st.session_state.is_authenticated:
        st.write(f"Вы вошли как: **{st.session_state.username}**")
        if st.button("Выйти"):
            logout_user()
            st.session_state.page = 'solution_list'
            st.rerun()
    else:
        if st.button("Вход / Регистрация"):
            st.session_state.page = 'auth'
            st.rerun()
    
    # App info
    st.markdown("---")
    st.markdown("""
    ### О проекте
    Визуальная библиотека решений для студентов, позволяющая делиться, изучать и комментировать решения заданий с пошаговым воспроизведением и поддержкой ИИ-ассистента.
    """)

# Main content area - render the appropriate page
if st.session_state.page == 'solution_list':
    solution_list_page()
elif st.session_state.page == 'solution_detail':
    solution_id = st.session_state.get('solution_id')
    if solution_id:
        solution_detail_page(solution_id)
    else:
        st.error("No solution selected.")
        st.session_state.page = 'solution_list'
        st.rerun()
elif st.session_state.page == 'upload_solution':
    upload_solution_form()
elif st.session_state.page == 'dashboard':
    dashboard_page()
elif st.session_state.page == 'auth':
    auth_page()
else:
    st.error("Unknown page.")
    st.session_state.page = 'solution_list'
    st.rerun()
