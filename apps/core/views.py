from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from .models import Institution
from .forms import InstitutionForm
from apps.users.models import User

class AdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.ADMIN:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class InstitutionListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Institution
    template_name = 'core/institution_list.html'
    context_object_name = 'institutions'

class InstitutionCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Institution
    form_class = InstitutionForm
    template_name = 'core/institution_form.html'
    success_url = reverse_lazy('core:institution_list')

class InstitutionUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Institution
    form_class = InstitutionForm
    template_name = 'core/institution_form.html'
    success_url = reverse_lazy('core:institution_list')
