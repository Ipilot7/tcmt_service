from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.tasks.models import Task
from apps.core.choices import StatusChoices
from django.utils import timezone
import datetime

class TaskAnalyticsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('task-analytics')

    def test_yearly_report_format(self):
        # Create some tasks in different months
        now = timezone.now()
        Task.objects.create(
            status=StatusChoices.NEW,
            description="Task 1",
            created_at=now
        )
        
        # Calculate last month using basic math
        last_month_year = now.year
        last_month = now.month - 1
        if last_month == 0:
            last_month = 12
            last_month_year -= 1
        last_month_date = now.replace(year=last_month_year, month=last_month)

        Task.objects.create(
            status=StatusChoices.NEW,
            description="Task 2",
            created_at=last_month_date
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertIn('yearly_report', data)
        self.assertEqual(len(data['yearly_report']), 12)
        
        current_month_str = now.strftime('%Y-%m')
        last_month_str = last_month_date.strftime('%Y-%m')
        
        report_dict = {item['month']: item['count'] for item in data['yearly_report']}
        
        self.assertEqual(report_dict.get(current_month_str), 1)
        self.assertEqual(report_dict.get(last_month_str), 1)
