from django.urls import path
from . import views

app_name = 'core' 

urlpatterns = [
    path('institutions/', views.InstitutionListView.as_view(), name='institution_list'),
    path('institutions/create/', views.InstitutionCreateView.as_view(), name='institution_create'),
    path('institutions/<int:pk>/update/', views.InstitutionUpdateView.as_view(), name='institution_update'),
    
    path('equipment/', views.EquipmentListView.as_view(), name='equipment_list'),
    path('equipment/create/', views.EquipmentCreateView.as_view(), name='equipment_create'),
    path('equipment/<int:pk>/update/', views.EquipmentUpdateView.as_view(), name='equipment_update'),
]
