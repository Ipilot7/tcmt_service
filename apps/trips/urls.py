from django.urls import path
from . import views

app_name = 'trips'

urlpatterns = [
    path('', views.TripListView.as_view(), name='list'),
    path('create/', views.TripCreateView.as_view(), name='create'),
    path('<int:pk>/', views.TripDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.TripUpdateView.as_view(), name='update'),
    path('<int:pk>/download/', views.download_trip_docx, name='download_docx'),
    path('export/', views.export_trips_to_excel, name='export'),
    path('import/', views.import_trips_from_excel, name='import'),
]
