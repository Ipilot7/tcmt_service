from django.urls import path
from . import views

app_name = 'requests'

urlpatterns = [
    path('', views.RequestListView.as_view(), name='list'),
    path('create/', views.RequestCreateView.as_view(), name='create'),
    path('<int:pk>/', views.RequestDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.RequestUpdateView.as_view(), name='update'),
    path('export/', views.export_requests_to_excel, name='export'),
    path('import/', views.import_requests_from_excel, name='import'),
]
