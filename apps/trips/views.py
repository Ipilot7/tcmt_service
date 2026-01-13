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


import openpyxl
from django.http import HttpResponse
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from apps.core.models import Region, Institution, EquipmentType, Status

def export_trips_to_excel(request):
    """
    Export all trips to an Excel file.
    """
    if request.user.role == User.Role.USER:
        raise PermissionDenied

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename=trips_export.xlsx'

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Trips'

    # Header row
    columns = [
        'Trip Number', 'Created At', 'Region', 'Institution',
        'Equipment Type', 'Status', 'Responsible', 'Contact Phone', 
        'Description', 'Escort Name', 'Escort Phone', 'Order Number', 'Result'
    ]
    worksheet.append(columns)

    for trip in Trip.objects.all().order_by('-created_at'):
        row = [
            trip.request_number,
            trip.created_at,
            trip.region.name if trip.region else '',
            trip.institution.name if trip.institution else '',
            trip.equipment_type.name if trip.equipment_type else '',
            trip.status.name if trip.status else '',
            trip.responsible.full_name if trip.responsible else '',
            trip.contact_phone,
            trip.description,
            trip.escort_name,
            trip.escort_phone,
            trip.order_number,
            trip.result_info
        ]
        worksheet.append(row)

    workbook.save(response)
    return response


def import_trips_from_excel(request):
    """
    Import trips from an Excel file.
    """
    if request.user.role == User.Role.USER:
        raise PermissionDenied

    if request.method == 'POST' and request.FILES.get('file'):
        excel_file = request.FILES['file']
        wb = openpyxl.load_workbook(excel_file)
        worksheet = wb.active

        # Start from second row
        for row in worksheet.iter_rows(min_row=2, values_only=True):
            # Maps to export:
            # 0: Number, 1: Created, 2: Region, 3: Institution, 4: Equip, 
            # 5: Status, 6: Resp, 7: Phone, 8: Desc, 9: EscortName, 
            # 10: EscortPhone, 11: Order, 12: Result
            
            region_name = row[2]
            institution_name = row[3]
            equipment_name = row[4]
            status_name = row[5]
            phone = row[7]
            desc = row[8]
            escort_name = row[9]
            escort_phone = row[10]
            order_num = row[11]
            result = row[12]

            region = Region.objects.filter(name__iexact=region_name).first()
            institution = Institution.objects.filter(name__iexact=institution_name).first()
            equipment = EquipmentType.objects.filter(name__iexact=equipment_name).first()
            status = Status.objects.filter(name__iexact=status_name).first()

            if region and institution and equipment and status:
                Trip.objects.create(
                    region=region,
                    institution=institution,
                    equipment_type=equipment,
                    status=status,
                    contact_phone=phone or '',
                    description=desc or '',
                    responsible=request.user,
                    escort_name=escort_name or '',
                    escort_phone=escort_phone or '',
                    order_number=order_num or '',
                    result_info=result or ''
                )
        
        return redirect('trips:list')

    return render(request, 'common/import_form.html')
