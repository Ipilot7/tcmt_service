from django.urls import path
from . import views

app_name = 'core' 

urlpatterns = [
    path('institutions/', views.InstitutionListView.as_view(), name='institution_list'),
    path('institutions/create/', views.InstitutionCreateView.as_view(), name='institution_create'),
    path('institutions/<int:pk>/update/', views.InstitutionUpdateView.as_view(), name='institution_update'),
]
