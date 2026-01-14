from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from .models import Institution
from .forms import InstitutionForm
from apps.users.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

class StaffRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in [User.Role.ADMIN, User.Role.MANAGER]:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class InstitutionListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Institution
    template_name = 'core/institution_list.html'
    context_object_name = 'institutions'
    paginate_by = 15

class InstitutionCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Institution
    form_class = InstitutionForm
    template_name = 'core/institution_form.html'
    success_url = reverse_lazy('core:institution_list')

class InstitutionUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Institution
    form_class = InstitutionForm
    template_name = 'core/institution_form.html'
    success_url = reverse_lazy('core:institution_list')

