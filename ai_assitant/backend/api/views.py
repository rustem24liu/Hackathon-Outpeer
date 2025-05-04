from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Category, Task, Solution, SolutionStep, AIChat, AIMessage
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework import status
# Сериализаторы
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'difficulty', 'category', 
                 'category_name', 'created_by', 'created_at']

class SolutionStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolutionStep
        fields = ['id', 'step_number', 'code_state', 'explanation']

class SolutionSerializer(serializers.ModelSerializer):
    steps = SolutionStepSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    class Meta:
        model = Solution
        fields = ['id', 'task', 'task_title', 'code', 'explanation', 
                 'author', 'is_ai_generated', 'created_at', 'steps']

class AIMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMessage
        fields = ['id', 'role', 'content', 'timestamp']

class AIChatSerializer(serializers.ModelSerializer):
    messages = AIMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = AIChat
        fields = ['id', 'title', 'created_at', 'messages']

# Представления API
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'category__name']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def solutions(self, request, pk=None):
        """Получить все решения для задания"""
        task = self.get_object()
        solutions = Solution.objects.filter(task=task)
        serializer = SolutionSerializer(solutions, many=True)
        return Response(serializer.data)

class SolutionViewSet(viewsets.ModelViewSet):
    queryset = Solution.objects.all()
    serializer_class = SolutionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

# В файле api/views.py - исправьте класс AIChatViewSet
class AIChatViewSet(viewsets.ModelViewSet):
    serializer_class = AIChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Получить чаты только текущего пользователя"""
        return AIChat.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        chat = serializer.save(user=self.request.user)
        
        # Создаем системное сообщение
        AIMessage.objects.create(
            chat=chat,
            role='system',
            content="Вы помощник в визуальной библиотеке решений задач. Помогайте пользователям с решением задач, объяснением алгоритмов и кода."
        )
    
    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        """Добавить сообщение в чат и получить ответ от ИИ"""
        chat = self.get_object()
        message_content = request.data.get('message', '')
        
        if not message_content:
            return Response({"error": "Сообщение не может быть пустым"}, 
                         status=status.HTTP_400_BAD_REQUEST)
        
        # Сохраняем сообщение пользователя
        user_msg = AIMessage.objects.create(
            chat=chat,
            role='user',
            content=message_content
        )
        
        # Имитация ответа от ИИ (заглушка)
        ai_content = "Ответ от ИИ-ассистента на ваше сообщение: " + message_content
        
        # Сохраняем ответ ассистента
        assistant_msg = AIMessage.objects.create(
            chat=chat,
            role='assistant',
            content=ai_content
        )
        
        # Возвращаем новые сообщения
        serializer = AIMessageSerializer(
            [user_msg, assistant_msg], 
            many=True
        )
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    return Response({'error': 'Неверное имя пользователя или пароль'}, status=400)