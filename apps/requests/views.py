from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from .models import Request
from .forms import RequestForm, RequestStatusForm
from apps.users.models import User
from apps.core.models import Status


# 🔒 Статусы, при которых обычный User не может редактировать
CLOSED_STATUSES = [
    'Выполнено',
    'Закрыто',
    'Отменено',
    'Completed',
    'Closed',
]


class RequestListView(LoginRequiredMixin, ListView):
    model = Request
    template_name = 'requests/list.html'
    context_object_name = 'requests'
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()

        q = self.request.GET.get('q')
        status_id = self.request.GET.get('status')

        if q:
            queryset = queryset.filter(
                Q(request_number__icontains=q) |
                Q(description__icontains=q) |
                Q(responsible__full_name__icontains=q)
            )

        if status_id and status_id.isdigit():
            queryset = queryset.filter(status_id=int(status_id))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        status = self.request.GET.get('status')
        context['selected_status'] = int(status) if status and status.isdigit() else None

        context['statuses'] = Status.objects.all()
        context['closed_statuses'] = CLOSED_STATUSES
        return context


class RequestDetailView(LoginRequiredMixin, DetailView):
    model = Request
    template_name = 'requests/detail.html'
    context_object_name = 'request_obj'


class RequestCreateView(LoginRequiredMixin, CreateView):
    model = Request
    form_class = RequestForm
    template_name = 'requests/form.html'
    success_url = reverse_lazy('requests:list')

    def dispatch(self, request, *args, **kwargs):
        if request.user.role == User.Role.USER:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.responsible = self.request.user
        return super().form_valid(form)


class RequestUpdateView(LoginRequiredMixin, UpdateView):
    model = Request
    template_name = 'requests/form.html'
    success_url = reverse_lazy('requests:list')

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        obj = self.object

        if request.user.role == User.Role.USER:
            if obj.status and obj.status.name in CLOSED_STATUSES:
                return redirect('requests:list')

        return response

    def get_form_class(self):
        if self.request.user.role == User.Role.USER:
            return RequestStatusForm
        return RequestForm
