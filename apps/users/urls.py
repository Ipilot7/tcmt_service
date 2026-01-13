from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

class CustomLoginView(LoginView):
    template_name = 'auth/login.html'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path(
        'logout/',
        LogoutView.as_view(
            next_page='/auth/login/'
        ),
        name='logout'
    ),
]
