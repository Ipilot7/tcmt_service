from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .models import Trip
from .forms import TripForm, TripStatusForm
from apps.users.models import User

from django.db.models import Q
from apps.core.models import Status

class TripListView(LoginRequiredMixin, ListView):
    model = Trip
    template_name = 'trips/list.html'
    context_object_name = 'trips'
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        status_id = self.request.GET.get('status')

        if q:
            queryset = queryset.filter(
                Q(request_number__icontains=q) |
                Q(description__icontains=q) |
                Q(responsible__full_name__icontains=q) |
                Q(escort_name__icontains=q)
            )
        
        if status_id:
            queryset = queryset.filter(status_id=status_id)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Status.objects.all()
        return context

class TripDetailView(LoginRequiredMixin, DetailView):
    model = Trip
    template_name = 'trips/detail.html'
    context_object_name = 'trip'

class TripCreateView(LoginRequiredMixin, CreateView):
    model = Trip
    form_class = TripForm
    template_name = 'trips/form.html'
    success_url = reverse_lazy('trips:list')

    def dispatch(self, request, *args, **kwargs):
        if request.user.role == User.Role.USER:
            return redirect('trips:list')
        return super().dispatch(request, *args, **kwargs)

class TripUpdateView(LoginRequiredMixin, UpdateView):
    model = Trip
    template_name = 'trips/form.html'
    success_url = reverse_lazy('trips:list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user.role == User.Role.USER:
            closed_statuses = ['Выполнено', 'Закрыто', 'Отменено', 'Completed', 'Closed']
            if obj.status.name in closed_statuses:
                return redirect('trips:list')
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        if self.request.user.role == User.Role.USER:
            return TripStatusForm
        return TripForm
