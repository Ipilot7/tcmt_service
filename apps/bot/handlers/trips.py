from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from asgiref.sync import sync_to_async
from apps.trips.models import Trip, TripResult
from apps.accounts.models import User
from apps.core.choices import StatusChoices

router = Router()

class TripStates(StatesGroup):
    waiting_for_report = State()

def get_trip_actions_kb(trip_id, current_status):
    buttons = []
    
    if current_status != StatusChoices.PENDING:
        buttons.append([InlineKeyboardButton(text="⏳ В работу", callback_data=f"trip_status:{trip_id}:{StatusChoices.PENDING}")])
    
    if current_status != StatusChoices.ON_HOLD:
        buttons.append([InlineKeyboardButton(text="⏸ На удержание", callback_data=f"trip_status:{trip_id}:{StatusChoices.ON_HOLD}")])
    
    if current_status != StatusChoices.COMPLETED:
        buttons.append([InlineKeyboardButton(text="✅ Завершить", callback_data=f"trip_complete:{trip_id}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(F.text == "🚗 Мои поездки")
async def list_user_trips(message: Message):
    user = await sync_to_async(lambda: User.objects.filter(telegram_id=str(message.from_user.id)).first())()
    if not user:
        await message.answer("❌ Сначала зарегистрируйтесь.")
        return

    # Получаем активные поездки
    trips = await sync_to_async(
        lambda: list(Trip.objects.filter(
            responsible_person=user
        ).exclude(status__in=[StatusChoices.COMPLETED, StatusChoices.CANCELED]).select_related('device_type')[:15])
    )()

    if not trips:
        await message.answer("🏝 <b>У вас нет активных поездок!</b>", parse_mode="HTML")
        return

    text = "🚗 <b>Ваши активные поездки:</b>\n"
    text += "────────────────────\n\n"
    for trip in trips:
        status_icon = "🆕" if trip.status == StatusChoices.NEW else "⏳" if trip.status == StatusChoices.PENDING else "⏸"
        text += (
            f"🆔 <b>№ {trip.task_number}</b>\n"
            f"🩺 {trip.device_type.name}\n"
            f"🚦 {status_icon} {trip.get_status_display()}\n"
            f"🔗 /trip_{trip.id}\n\n"
        )
    
    await message.answer(text, parse_mode="HTML")

@router.message(F.text.startswith("/trip_"))
async def show_trip_detail(message: Message):
    trip_id = message.text.split("_")[1]
    user = await sync_to_async(lambda: User.objects.filter(telegram_id=str(message.from_user.id)).first())()
    
    trip = await sync_to_async(
        lambda: Trip.objects.filter(id=trip_id, responsible_person=user).select_related('device_type', 'hospital').first()
    )()

    if not trip:
        await message.answer("❌ Поездка не найдена или у вас нет к ней доступа.")
        return

    text = (
        f"🚗 <b>ПОЕЗДКА № {trip.task_number}</b>\n"
        "────────────────────\n\n"
        f"📍 <b>Локация:</b>\n└ {trip.hospital.name}\n\n"
        f"🩺 <b>Оборудование:</b>\n└ {trip.device_type.name}\n\n"
        f"📝 <b>Задача:</b>\n{trip.description}\n\n"
        f"📞 <b>Контакты:</b> {trip.contact_phone}\n\n"
        f"📅 <b>Дата поездки:</b> {trip.trip_date or 'Не указана'}\n"
        f"🚦 <b>Текущий статус:</b> <u>{trip.get_status_display()}</u>\n"
    )

    await message.answer(text, reply_markup=get_trip_actions_kb(trip.id, trip.status), parse_mode="HTML")

@router.callback_query(F.data.startswith("trip_status:"))
async def change_trip_status(callback: CallbackQuery):
    _, trip_id, new_status = callback.data.split(":")
    
    trip = await sync_to_async(lambda: Trip.objects.filter(id=trip_id).first())()
    if trip:
        trip.status = new_status
        await sync_to_async(trip.save)()
        await callback.answer("🔄 Статус обновлен!")
        await callback.message.edit_reply_markup(reply_markup=get_trip_actions_kb(trip.id, trip.status))
    else:
        await callback.answer("❌ Ошибка!")

@router.callback_query(F.data.startswith("trip_complete:"))
async def start_trip_completion(callback: CallbackQuery, state: FSMContext):
    trip_id = callback.data.split(":")[1]
    await state.set_state(TripStates.waiting_for_report)
    await state.update_data(trip_id=trip_id)
    
    await callback.message.answer(
        "📝 Пожалуйста, напишите краткий <b>отчет о проделанной работе</b> для завершения поездки:",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(TripStates.waiting_for_report)
async def process_trip_report(message: Message, state: FSMContext):
    data = await state.get_data()
    trip_id = data['trip_id']
    report = message.text.strip()
    
    trip = await sync_to_async(lambda: Trip.objects.filter(id=trip_id).first())()
    if trip:
        # Для Trip используем TripResult
        await sync_to_async(
            lambda: TripResult.objects.update_or_create(trip=trip, defaults={'result_info': report})
        )()
        
        trip.status = StatusChoices.COMPLETED
        await sync_to_async(trip.save)()
        
        await message.answer(
            f"✅ <b>Поездка {trip.task_number} успешно завершена!</b>\nОтчет сохранен.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
    else:
        await message.answer("❌ Ошибка: поездка не найдена.")
    
    await state.clear()
