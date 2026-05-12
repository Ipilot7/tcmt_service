from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import Device

class DeviceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.serial_number = self.scope['url_route']['kwargs'].get('serial_number')
        
        # Если подключается клиент карты (Flutter) для прослушивания всех устройств
        if self.serial_number == 'all':
            self.room_group_name = 'map_updates'
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            return

        # Иначе это подключается конкретное устройство (или клиент, слушающий одно устройство)
        self.device = await self.get_device(self.serial_number)
        
        if not self.device:
            await self.close(code=4004)
            return

        # Обновляем статус в БД
        await self.set_device_online_status(self.device, True)

        # Используем ID устройства для имени группы, так как серийный номер может содержать кириллицу или "/"
        self.room_group_name = f'device_{self.device.id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        # Опционально: можно сразу отправить статус "online" всем слушателям
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'device_status_update',
                'status': 'online',
                'serial_number': self.serial_number
            }
        )

        # Оповещаем слушателей карты
        await self.channel_layer.group_send(
            'map_updates',
            {
                'type': 'map_status_update',
                'status': 'online',
                'serial_number': self.serial_number
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            # Если это было конкретное устройство (а не слушатель всех устройств)
            if self.serial_number != 'all' and hasattr(self, 'device'):
                await self.set_device_online_status(self.device, False)
                
                # Уведомляем тех, кто слушает конкретное устройство
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'device_status_update',
                        'status': 'offline',
                        'serial_number': self.serial_number
                    }
                )
                
                # Оповещаем слушателей карты
                await self.channel_layer.group_send(
                    'map_updates',
                    {
                        'type': 'map_status_update',
                        'status': 'offline',
                        'serial_number': self.serial_number
                    }
                )
            
            # Покидаем группу
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # Получение сообщения от самого оборудования (или клиента)
    async def receive(self, text_data):
        data = json.loads(text_data)
        
        # Например, устройство отправляет {"action": "status", "data": {"temp": 45, "error": null}}
        action = data.get('action')
        payload = data.get('data', {})

        if action == 'status':
            # Пересылаем статус всем, кто слушает это устройство (страница устройства)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'device_data_update',
                    'serial_number': self.serial_number,
                    'data': payload
                }
            )
            
            # Также пересылаем статус на общую карту
            await self.channel_layer.group_send(
                'map_updates',
                {
                    'type': 'device_data_update',
                    'serial_number': self.serial_number,
                    'data': payload
                }
            )

    # Обработчики для рассылки в WebSocket
    async def device_status_update(self, event):
        await self.send(text_data=json.dumps({
            'event': 'status_change',
            'serial_number': event['serial_number'],
            'status': event['status']
        }))

    async def device_data_update(self, event):
        # Отправляем во Flutter только серийный номер и статус
        await self.send(text_data=json.dumps({
            'serial_number': event['serial_number'],
            'status': event['data'].get('status', 'online')
        }))

    # Новый обработчик для отправки команд на устройство
    async def device_command(self, event):
        # Этот метод вызывается, когда мы отправляем сообщение в группу устройства
        # через channel_layer.group_send(group_name, {"type": "device_command", "command": "..."})
        await self.send(text_data=json.dumps({
            'command': event['command']
        }))

    async def map_status_update(self, event):
        await self.send(text_data=json.dumps({
            'event': 'status_change',
            'serial_number': event['serial_number'],
            'status': event['status']
        }))

    @database_sync_to_async
    def get_device(self, serial_number):
        try:
            return Device.objects.get(serial_number=serial_number)
        except Device.DoesNotExist:
            return None

    @database_sync_to_async
    def set_device_online_status(self, device, is_online):
        device.is_online = is_online
        device.save(update_fields=['is_online'])
