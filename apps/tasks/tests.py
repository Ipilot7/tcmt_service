from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.tasks.models import Task
from apps.core.choices import StatusChoices
from django.utils import timezone
from dateutil.relativedelta import relativedelta

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
        Task.objects.create(
            status=StatusChoices.NEW,
            description="Task 2",
            created_at=now - relativedelta(months=1)
        )
        Task.objects.create(
            status=StatusChoices.NEW,
            description="Task 3",
            created_at=now - relativedelta(months=13) # Should be excluded from last 12 months
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertIn('yearly_report', data)
        self.assertEqual(len(data['yearly_report']), 12)
        
        # Check if the counts are correct for the last checkable months
        # Note: the test might be sensitive to the exact day of the month if not careful,
        # but the aggregation uses TruncMonth.
        
        current_month = now.strftime('%Y-%m')
        last_month = (now - relativedelta(months=1)).strftime('%Y-%m')
        
        # Find these months in the report
        report_dict = {item['month']: item['count'] for item in data['yearly_report']}
        
        # We can't guarantee the exact order without strictly checking the loop logic,
        # but the list should contain 12 items.
        self.assertEqual(report_dict.get(current_month), 1)
        self.assertEqual(report_dict.get(last_month), 1)
