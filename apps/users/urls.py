from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from apps.users.views import UserListView, UserCreateView, UserUpdateView

app_name = 'users'

class CustomLoginView(LoginView):
    template_name = 'auth/login.html'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/auth/login/'), name='logout'),
    
    path('list/', UserListView.as_view(), name='list'),
    path('create/', UserCreateView.as_view(), name='create'),
    path('<int:pk>/update/', UserUpdateView.as_view(), name='update'),
]
