from django.urls import path
from .views import RegisterView, LoginView, AddTask, ViewTask, login_view, dashboard, addnewtask

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('addtask', AddTask.as_view()),
    path('viewtask', ViewTask.as_view()),

    path('', login_view, name='index'),   
    path('dashboard/<int:id>', dashboard, name='dashboard'),  
    path('addnewtask/<int:id>', addnewtask, name='addtask'),
    
]