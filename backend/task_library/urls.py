from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import CategoryViewSet, TaskViewSet, SolutionViewSet, AIChatViewSet, login_view

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'solutions', SolutionViewSet)
router.register(r'ai-chats', AIChatViewSet, basename='ai-chats')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api/auth/login/', login_view, name='login'),
]