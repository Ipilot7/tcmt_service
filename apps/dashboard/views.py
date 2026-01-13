from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import datetime, timedelta
from apps.requests.models import Request
from apps.trips.models import Trip
from apps.users.models import User

@login_required
def index(request):
    return render(request, 'dashboard/index.html')

@login_required
def statistics(request):
    # Default: Last 30 days
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    user_id = request.GET.get('user_id')

    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')

    users = User.objects.all()
    
    # Filter QuerySets
    req_qs = Request.objects.filter(created_at__range=[start_date, end_date])
    trip_qs = Trip.objects.filter(created_at__range=[start_date, end_date])

    if user_id:
        req_qs = req_qs.filter(responsible_id=user_id)
        trip_qs = trip_qs.filter(responsible_id=user_id)

    # Calculate Stats
    # Assuming 'Done' statuses. You might want to adjust this list.
    done_statuses = ['Выполнено', 'Закрыто', 'Completed', 'Closed']

    req_total = req_qs.count()
    req_done = req_qs.filter(status__name__in=done_statuses).count()
    
    trip_total = trip_qs.count()
    trip_done = trip_qs.filter(status__name__in=done_statuses).count()

    context = {
        'users': users,
        'start_date': start_date,
        'end_date': end_date,
        'selected_user': int(user_id) if user_id else None,
        'req_total': req_total,
        'req_done': req_done,
        'trip_total': trip_total,
        'trip_done': trip_done,
        'requests': req_qs,
        'trips': trip_qs,
    }

    return render(request, 'dashboard/statistics.html', context)
