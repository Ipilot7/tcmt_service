import asyncio
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

# Import handlers (I will create them next)
from apps.bot.handlers import auth, tasks, trips

class Command(BaseCommand):
    help = 'Runs the Telegram bot'

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        asyncio.run(self.main())

    async def main(self):
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stderr.write("TELEGRAM_BOT_TOKEN is not set in settings!")
            return

        bot = Bot(
            token=settings.TELEGRAM_BOT_TOKEN, 
            default=DefaultBotProperties(parse_mode="HTML")
        )
        dp = Dispatcher(storage=MemoryStorage())

        # Include routers
        dp.include_router(auth.router)
        dp.include_router(tasks.router)
        dp.include_router(trips.router)

        self.stdout.write("Starting bot...")
        await dp.start_polling(bot)
