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

    def test_month_filtering_and_categories(self):
        from apps.tasks.models import TaskCategory
        from apps.devices.models import DeviceType
        from apps.locations.models import Hospital

        # Create prerequisites
        hospital = Hospital.objects.create(name="Test Hospital")
        dt1 = DeviceType.objects.create(name="Device 1")
        dt2 = DeviceType.objects.create(name="Device 2")
        cat1 = TaskCategory.objects.create(name="IT")
        cat2 = TaskCategory.objects.create(name="Technical")

        # Create tasks in January 2026
        jan_date = datetime.date(2026, 1, 15)
        Task.objects.create(hospital=hospital, device_type=dt1, category=cat1, description="T1", created_at=jan_date)
        Task.objects.create(hospital=hospital, device_type=dt1, category=cat2, description="T2", created_at=jan_date)
        Task.objects.create(hospital=hospital, device_type=dt2, category=cat1, description="T3", created_at=jan_date)

        # Create a task in February 2026
        feb_date = datetime.date(2026, 2, 10)
        Task.objects.create(hospital=hospital, device_type=dt1, category=cat1, description="T4", created_at=feb_date)

        # Test January 2026
        response = self.client.get(self.url, {'month': '2026-01'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 3)
        
        breakdown = response.data['breakdown']
        self.assertEqual(len(breakdown), 2)
        
        # Check dt1 (2 tasks in Jan)
        dt1_item = next(item for item in breakdown if item['label'] == "Device 1")
        self.assertEqual(dt1_item['count'], 2)
        self.assertEqual(len(dt1_item['categories']), 2)
        cat_labels = [c['label'] for c in dt1_item['categories']]
        self.assertIn("IT", cat_labels)
        self.assertIn("Technical", cat_labels)

        # Test February 2026
        response = self.client.get(self.url, {'month': '2026-02'})
        self.assertEqual(response.data['total'], 1)
        self.assertEqual(len(response.data['breakdown']), 1)
        self.assertEqual(response.data['breakdown'][0]['label'], "Device 1")
        self.assertEqual(response.data['breakdown'][0]['count'], 1)
