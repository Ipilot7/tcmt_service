from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('stats/', views.statistics, name='stats'),
    path('user-stats/', views.user_statistics, name='user-stats'),
]
