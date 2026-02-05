from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.models import FCMToken, Role
from apps.tasks.models import Task
from apps.trips.models import Trip
from apps.locations.models import Hospital
from apps.devices.models import DeviceType
from unittest.mock import patch

User = get_user_model()

class NotificationSignalTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(login='testuser', password='password', fullname='Test User')
        self.manager = User.objects.create_user(login='manager', password='password', fullname='Manager User')
        self.manager_role, _ = Role.objects.get_or_create(name='Manager')
        self.manager.roles.add(self.manager_role)
        
        self.hospital = Hospital.objects.create(name='Test Hospital')
        self.device_type = DeviceType.objects.create(name='Test Device')
        
        FCMToken.objects.create(user=self.user, token='token1')
        FCMToken.objects.create(user=self.manager, token='token_manager')

    @patch('apps.core.notifications.send_push_notification')
    def test_task_creation_notification(self, mock_send):
        Task.objects.create(
            hospital=self.hospital,
            device_type=self.device_type,
            description='Test Task',
            responsible_person=self.user
        )
        self.assertTrue(mock_send.called)
        # Check if called with correct user
        args, kwargs = mock_send.call_args
        self.assertEqual(kwargs['user'], self.user)

    @patch('apps.core.notifications.send_push_notification')
    def test_trip_creation_notification(self, mock_send):
        Trip.objects.create(
            hospital=self.hospital,
            device_type=self.device_type,
            description='Test Trip',
            contact_phone='12345678',
            responsible_person=self.user
        )
        self.assertTrue(mock_send.called)
        args, kwargs = mock_send.call_args
        self.assertEqual(kwargs['user'], self.user)

    @patch('apps.core.notifications.notify_managers')
    def test_task_status_change_notification(self, mock_notify):
        task = Task.objects.create(
            hospital=self.hospital,
            device_type=self.device_type,
            description='Test Task',
            responsible_person=self.user
        )
        # Reset mock after creation
        mock_notify.reset_mock()
        
        task.status = 'CP' # Completed
        task.save()
        
        self.assertTrue(mock_notify.called)
        args, kwargs = mock_notify.call_args
        self.assertIn('Статус задачи', args[0])
