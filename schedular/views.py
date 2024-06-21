from django.shortcuts import render

#API
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer, TaskSerializer
from django.http import HttpResponse
from .models import User, Task
import jwt
import datetime



# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': "User created successfully", 'details': serializer.data})


class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.now(datetime.timezone.utc)
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        return Response({'jwt': token})


class AddTask(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    

class ViewTask(APIView):

    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        usertasks = Task.objects.filter(assigned_to = payload['id'])
        serializer = TaskSerializer(usertasks, many=True)
        return Response(serializer.data)
    


#TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import LoginForm
from .models import Task

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                person = User.objects.get(email = user)
                id = person.id
                return redirect(f'dashboard/{id}')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def dashboard(request, id):
    mydata = Task.objects.filter(assigned_to = id)
    user = User.objects.get(id = id)
    all_users = User.objects.all()
    if(mydata!=''):
        return render(request, 'dashboard.html', {'mydatas' : mydata, 'user': user, 'all_users': all_users})
    else:
        return render(request,'dashboard.html', {'user': user, 'all_users': all_users})
    
def addnewtask(request, id):
    if request.method == 'POST':
        print(request.POST)
        name = request.POST['name']
        date_time = request.POST['date_time']
        assigned_to = request.POST['assigned_to']
        print(request.POST['assigned_to'][0])
        assigned_by = id
        status = request.POST['status']

        obj = Task()
        obj.name = name
        obj.date_time = date_time
        obj.assigned_to = User.objects.get(id = assigned_to[0])
        obj.assigned_by = User.objects.get(id = id)
        obj.status = status

        obj.save()
        return redirect(f'/view/dashboard/{id}')
    
    all_users = User.objects.all()
    user = User.objects.get(id = id)
    return render(request,'addtask.html', {'all_users': all_users, 'user': user})
