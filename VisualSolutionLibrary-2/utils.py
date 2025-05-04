import os
import json
import base64
import uuid
import openai
from openai import OpenAI
from datetime import datetime
from pathlib import Path
import pygments
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer

import os


# Create necessary directories if they don't exist
def ensure_directories():
    """Ensure all necessary directories exist"""
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/uploads", exist_ok=True)
    
    # Create initial JSON files if they don't exist
    for file_name in ["solutions.json", "users.json", "comments.json", "ratings.json"]:
        file_path = f"data/{file_name}"
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                json.dump([], f)



key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=key)

# Initialize OpenAI API
def init_openai_api():
    """Initialize OpenAI API with API key from environment variables"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        openai.api_key = api_key
        return True
    return False

# Get code explanation from OpenAI
def get_code_explanation_from_ai(code, language=None):
    """Get code explanation from OpenAI"""
    # if not init_openai_api():
    #     return "ИИ-ассистент недоступен. Пожалуйста, добавьте API ключ OpenAI в настройках."
    #
    try:
        # Use OpenAI API for code explanation

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты - учsебный ассистент, который объясняет код ясным и понятным языком. Пиши свои пояснения на русском языке."},
                {"role": "user", "content": f"Объясни следующий код на языке {language or 'программирования'} студенту, который только изучает программирование:\n\n{code}"}
            ],
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка при получении объяснения от ИИ: {str(e)}"

# Generate a unique ID for new items
def generate_id():
    """Generate a unique ID"""
    return str(uuid.uuid4())

# Format timestamp
def format_timestamp(timestamp):
    """Format timestamp in a readable format"""
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# Get current timestamp
def get_timestamp():
    """Get current timestamp"""
    return datetime.now().timestamp()

# Highlight code with syntax highlighting
def highlight_code(code, language=None):
    """Highlight code with syntax highlighting"""
    try:
        if language:
            lexer = get_lexer_by_name(language)
        else:
            # Попытаемся угадать язык, если он не указан
            try:
                lexer = guess_lexer(code)
            except:
                # Если не смогли угадать, используем Python по умолчанию
                lexer = get_lexer_by_name("python")
        
        # Используем более контрастный стиль с подсветкой
        formatter = HtmlFormatter(
            style="monokai",  # Стиль с яркими цветами как на изображении
            cssclass="highlight",
            linenos=False,    # Без номеров строк
            noclasses=True,   # Встраиваем стили непосредственно
            nowrap=False      # Переносим длинные строки
        )
        
        return pygments.highlight(code, lexer, formatter)
    except Exception:
        # Return plain code if highlighting fails
        return f"<pre>{code}</pre>"

# Get CSS for syntax highlighting
def get_highlighting_css():
    """Get CSS for syntax highlighting"""
    formatter = HtmlFormatter(style="monokai")
    return formatter.get_style_defs('.highlight')

# File extension to language mapping
def get_language_from_extension(file_path):
    """Get language from file extension"""
    extension_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.html': 'html',
        '.css': 'css',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
        '.php': 'php',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.ts': 'typescript',
        '.sql': 'sql',
        '.sh': 'bash',
    }
    ext = Path(file_path).suffix
    return extension_map.get(ext.lower(), None)

# Read file contents
def read_file(file_path):
    """Read file contents"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

# Save uploaded file
def save_uploaded_file(uploaded_file, solution_id):
    """Save uploaded file to disk and return the saved path"""
    file_ext = Path(uploaded_file.name).suffix
    file_path = f"data/uploads/{solution_id}{file_ext}"
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

# Calculate average rating
def calculate_average_rating(ratings, solution_id):
    """Calculate average rating for a solution"""
    solution_ratings = [r['rating'] for r in ratings if r['solution_id'] == solution_id]
    if solution_ratings:
        return sum(solution_ratings) / len(solution_ratings)
    return 0

# Parse solution into steps
def parse_solution_steps(file_path):
    """Parse solution into steps based on common markers or line breaks"""
    content = read_file(file_path)
    
    # Try to split by common step markers
    step_markers = ["# Step", "// Step", "-- Step", "/* Step"]
    
    for marker in step_markers:
        if marker in content:
            steps = content.split(marker)
            # Remove empty steps and clean up
            steps = [step.strip() for step in steps if step.strip()]
            if steps:
                return steps
    
    # If no markers found, split by lines with reasonable grouping
    lines = content.split('\n')
    steps = []
    current_step = []
    
    for line in lines:
        current_step.append(line)
        if len(current_step) >= 10 or (line.strip() == '' and len(current_step) > 3):
            steps.append('\n'.join(current_step))
            current_step = []
    
    if current_step:
        steps.append('\n'.join(current_step))
    
    return steps if steps else [content]

# Get file display name
def get_display_name(file_path):
    """Get the display name for a file"""
    return os.path.basename(file_path)
