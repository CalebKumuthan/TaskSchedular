from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Task

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'assigned_to', 'status']
