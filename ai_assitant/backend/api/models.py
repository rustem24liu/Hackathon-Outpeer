# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    """Категории заданий"""
    name = models.CharField(_("Название"), max_length=100)
    description = models.TextField(_("Описание"), blank=True)
    
    def __str__(self):
        return self.name

class Task(models.Model):
    """Модель для хранения заданий"""
    DIFFICULTY_CHOICES = [
        ('easy', _('Легкий')),
        ('medium', _('Средний')),
        ('hard', _('Сложный')),
    ]
    
    title = models.CharField(_("Заголовок"), max_length=200)
    description = models.TextField(_("Описание"))
    difficulty = models.CharField(_("Сложность"), max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    category = models.ForeignKey(Category, verbose_name=_("Категория"), related_name="tasks", on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, verbose_name=_("Создатель"), related_name="created_tasks", on_delete=models.CASCADE)
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Дата обновления"), auto_now=True)
    
    def __str__(self):
        return self.title

class Solution(models.Model):
    """Модель для хранения решений заданий"""
    task = models.ForeignKey(Task, verbose_name=_("Задание"), related_name="solutions", on_delete=models.CASCADE)
    code = models.TextField(_("Код решения"))
    explanation = models.TextField(_("Объяснение"), blank=True)
    author = models.ForeignKey(User, verbose_name=_("Автор"), related_name="solutions", on_delete=models.CASCADE)
    is_ai_generated = models.BooleanField(_("Сгенерировано ИИ"), default=False)
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    
    def __str__(self):
        return f"Решение для {self.task.title}"

class SolutionStep(models.Model):
    """Шаги решения для пошагового воспроизведения"""
    solution = models.ForeignKey(Solution, verbose_name=_("Решение"), related_name="steps", on_delete=models.CASCADE)
    step_number = models.PositiveIntegerField(_("Номер шага"))
    code_state = models.TextField(_("Состояние кода"))
    explanation = models.TextField(_("Объяснение шага"))
    
    class Meta:
        ordering = ['step_number']
    
    def __str__(self):
        return f"Шаг {self.step_number} решения {self.solution.id}"

class AIChat(models.Model):
    """История чатов с ИИ-ассистентом"""
    user = models.ForeignKey(User, related_name="ai_chats", on_delete=models.CASCADE)
    title = models.CharField(_("Название"), max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class AIMessage(models.Model):
    """Сообщения в чате с ИИ"""
    ROLE_CHOICES = [
        ('user', _('Пользователь')),
        ('assistant', _('Ассистент')),
        ('system', _('Система')),
    ]
    
    chat = models.ForeignKey(AIChat, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(_("Роль"), max_length=10, choices=ROLE_CHOICES)
    content = models.TextField(_("Содержание"))
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.get_role_display()} ({self.timestamp})"