from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied

from .models import Institution, Equipment
from .forms import InstitutionForm, EquipmentForm
from .selectors import get_institutions_list, get_equipment_list
from .services import institution_create, institution_update, equipment_create, equipment_update
from .serializers import InstitutionSerializer, EquipmentSerializer
from apps.users.models import User

class StaffRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.MANAGER]:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class InstitutionListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    template_name = 'core/institution_list.html'
    context_object_name = 'institutions'
    paginate_by = 15

    def get_queryset(self):
        return get_institutions_list()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Сериализуем объекты для единообразия данных в шаблонах
        context['institutions_serialized'] = InstitutionSerializer.serialize_list(context['institutions'])
        return context

class InstitutionCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Institution
    form_class = InstitutionForm
    template_name = 'core/institution_form.html'
    success_url = reverse_lazy('core:institution_list')

    def form_valid(self, form):
        institution_create(**form.cleaned_data)
        return redirect(self.success_url)

class InstitutionUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Institution
    form_class = InstitutionForm
    template_name = 'core/institution_form.html'
    success_url = reverse_lazy('core:institution_list')

    def form_valid(self, form):
        institution_update(institution=self.object, **form.cleaned_data)
        return redirect(self.success_url)

class EquipmentListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    template_name = 'core/equipment_list.html'
    context_object_name = 'equipments'
    paginate_by = 15

    def get_queryset(self):
        return get_equipment_list()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Сериализуем объекты для единообразия данных в шаблонах
        context['equipments_serialized'] = EquipmentSerializer.serialize_list(context['equipments'])
        return context

class EquipmentCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'core/equipment_form.html'
    success_url = reverse_lazy('core:equipment_list')

    def form_valid(self, form):
        equipment_create(**form.cleaned_data)
        return redirect(self.success_url)

class EquipmentUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'core/equipment_form.html'
    success_url = reverse_lazy('core:equipment_list')

    def form_valid(self, form):
        equipment_update(equipment=self.object, **form.cleaned_data)
        return redirect(self.success_url)
