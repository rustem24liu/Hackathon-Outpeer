import hashlib
import secrets
import streamlit as st
from data_manager import get_user_by_username, add_user

def hash_password(password, salt=None):
    """Hash a password with a salt for secure storage"""
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Hash password with salt
    pwdhash = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt.encode('utf-8'), 
        100000
    ).hex()
    
    return f"{salt}${pwdhash}"

def verify_password(stored_password, provided_password):
    """Verify a password against a stored hash"""
    salt, stored_hash = stored_password.split('$')
    return stored_password == hash_password(provided_password, salt)

def initialize_session_state():
    """Initialize session state variables for authentication"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False

def login_user(username, password):
    """Log in a user with username and password"""
    user = get_user_by_username(username)
    if user and verify_password(user['password_hash'], password):
        st.session_state.user_id = user['id']
        st.session_state.username = user['username']
        st.session_state.is_authenticated = True
        return True
    return False

def register_user(username, password):
    """Register a new user"""
    # Check if username already exists
    if get_user_by_username(username):
        return False
    
    # Hash password and add user
    password_hash = hash_password(password)
    user_id = add_user(username, password_hash)
    
    if user_id:
        # Auto-login after registration
        st.session_state.user_id = user_id
        st.session_state.username = username
        st.session_state.is_authenticated = True
        return True
    
    return False

def logout_user():
    """Log out the current user"""
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.is_authenticated = False

def require_auth():
    """Check if user is authenticated, if not redirect to login page"""
    if not st.session_state.is_authenticated:
        st.warning("Необходимо войти в систему для доступа к этой функции.")
        return False
    return True

def auth_page():
    """Display authentication page with login and registration"""
    st.title("Аутентификация")
    
    tab1, tab2 = st.tabs(["Вход", "Регистрация"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Имя пользователя")
            password = st.text_input("Пароль", type="password")
            submit_button = st.form_submit_button("Войти")
            
            if submit_button:
                if username and password:
                    if login_user(username, password):
                        st.success("Вход выполнен успешно!")
                        st.rerun()
                    else:
                        st.error("Неверное имя пользователя или пароль.")
                else:
                    st.error("Пожалуйста, введите имя пользователя и пароль.")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Придумайте имя пользователя")
            new_password = st.text_input("Придумайте пароль", type="password")
            confirm_password = st.text_input("Подтвердите пароль", type="password")
            register_button = st.form_submit_button("Зарегистрироваться")
            
            if register_button:
                if not new_username or not new_password:
                    st.error("Пожалуйста, заполните все поля.")
                elif new_password != confirm_password:
                    st.error("Пароли не совпадают.")
                elif len(new_password) < 6:
                    st.error("Пароль должен содержать не менее 6 символов.")
                else:
                    if register_user(new_username, new_password):
                        st.success("Регистрация прошла успешно! Вы вошли в систему.")
                        st.rerun()
                    else:
                        st.error("Имя пользователя уже существует. Пожалуйста, выберите другое.")
