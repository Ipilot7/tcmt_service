from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from asgiref.sync import sync_to_async
from django.utils import timezone

from apps.accounts.models import User
from apps.bot.keyboards.main import get_main_menu
from apps.core.choices import StatusChoices
from apps.trips.models import Trip, TripResult

router = Router()


class TripStates(StatesGroup):
    waiting_for_report = State()


def build_trip_report(report: str, target_status: str) -> str:
    report_label = "ПРИЧИНА УДЕРЖАНИЯ" if target_status == StatusChoices.ON_HOLD else "ОТЧЕТ"
    report_time = timezone.localtime().strftime("%d.%m.%Y %H:%M")
    return f"--- {report_label} ---\nВремя отчета: {report_time}\n{report}"


def get_trip_device_type_name(trip: Trip) -> str:
    return trip.device_type.name if trip.device_type else "Не указано"


def get_trip_actions_kb(trip_id, current_status):
    buttons = []

    if current_status != StatusChoices.PENDING:
        buttons.append(
            [InlineKeyboardButton(text="⏳ В работу", callback_data=f"trip_status:{trip_id}:{StatusChoices.PENDING}")]
        )

    if current_status != StatusChoices.ON_HOLD:
        buttons.append(
            [InlineKeyboardButton(text="⏸ На удержание", callback_data=f"trip_status:{trip_id}:{StatusChoices.ON_HOLD}")]
        )

    if current_status != StatusChoices.COMPLETED:
        buttons.append([InlineKeyboardButton(text="✅ Завершить", callback_data=f"trip_complete:{trip_id}")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text == "🚗 Мои поездки")
async def list_user_trips(message: Message):
    user = await sync_to_async(lambda: User.objects.filter(telegram_id=str(message.from_user.id)).first())()
    if not user:
        await message.answer("❌ Сначала зарегистрируйтесь.")
        return

    trips = await sync_to_async(
        lambda: list(
            Trip.objects.filter(responsible_persons=user)
            .exclude(status__in=[StatusChoices.COMPLETED, StatusChoices.CANCELED])
            .select_related("device_type")[:15]
        )
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
            f"🩺 {get_trip_device_type_name(trip)}\n"
            f"🚦 {status_icon} {trip.get_status_display()}\n"
            f"🔗 /trip_{trip.id}\n\n"
        )

    await message.answer(text, parse_mode="HTML")


@router.message(F.text.startswith("/trip_"))
async def show_trip_detail(message: Message):
    trip_id = message.text.split("_")[1]
    user = await sync_to_async(lambda: User.objects.filter(telegram_id=str(message.from_user.id)).first())()

    trip = await sync_to_async(
        lambda: Trip.objects.filter(id=trip_id, responsible_persons=user)
        .select_related("device_type", "hospital")
        .first()
    )()

    if not trip:
        await message.answer("❌ Поездка не найдена или у вас нет к ней доступа.")
        return

    responsibles = await sync_to_async(lambda: ", ".join([u.fullname for u in trip.responsible_persons.all()]))()
    hospital_name = trip.hospital.name if trip.hospital else "Не указана"

    text = (
        f"🚗 <b>ПОЕЗДКА № {trip.task_number}</b>\n"
        "────────────────────\n\n"
        f"👥 <b>Ответственные:</b>\n└ {responsibles}\n\n"
        f"📍 <b>Локация:</b>\n└ {hospital_name}\n\n"
        f"🩺 <b>Оборудование:</b>\n└ {get_trip_device_type_name(trip)}\n\n"
        f"📝 <b>Задача:</b>\n{trip.description}\n\n"
        f"📞 <b>Контакты:</b> {trip.contact_phone or 'Не указаны'}\n\n"
        f"📅 <b>Дата поездки:</b> {trip.trip_date or 'Не указана'}\n"
        f"🚦 <b>Текущий статус:</b> <u>{trip.get_status_display()}</u>\n"
    )

    await message.answer(text, reply_markup=get_trip_actions_kb(trip.id, trip.status), parse_mode="HTML")


@router.callback_query(F.data.startswith("trip_status:"))
async def change_trip_status(callback: CallbackQuery, state: FSMContext):
    _, trip_id, new_status = callback.data.split(":")

    if new_status == StatusChoices.ON_HOLD:
        await state.set_state(TripStates.waiting_for_report)
        await state.update_data(trip_id=trip_id, target_status=new_status)
        await callback.message.answer(
            "📝 Пожалуйста, напишите <b>причину перевода поездки на удержание</b>: ",
            parse_mode="HTML",
        )
        await callback.answer()
        return

    trip = await sync_to_async(lambda: Trip.objects.filter(id=trip_id).first())()
    if trip:
        trip.status = new_status
        await sync_to_async(trip.save)()
        await callback.answer("🔄 Статус обновлен!")

        base_text = callback.message.text.split("🚦")[0]
        new_text = base_text + f"🚦 <b>Текущий статус:</b> <u>{trip.get_status_display()}</u>"

        await callback.message.edit_text(
            new_text,
            parse_mode="HTML",
            reply_markup=get_trip_actions_kb(trip.id, trip.status),
        )
    else:
        await callback.answer("❌ Ошибка!")


@router.callback_query(F.data.startswith("trip_complete:"))
async def start_trip_completion(callback: CallbackQuery, state: FSMContext):
    trip_id = callback.data.split(":")[1]
    await state.set_state(TripStates.waiting_for_report)
    await state.update_data(trip_id=trip_id, target_status=StatusChoices.COMPLETED)

    await callback.message.answer(
        "📝 Пожалуйста, напишите краткий <b>отчет о проделанной работе</b> для завершения поездки:",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(TripStates.waiting_for_report)
async def process_trip_report(message: Message, state: FSMContext):
    data = await state.get_data()
    trip_id = data["trip_id"]
    target_status = data.get("target_status", StatusChoices.COMPLETED)
    report = message.text.strip()

    trip = await sync_to_async(lambda: Trip.objects.filter(id=trip_id).first())()
    if trip:
        report_entry = build_trip_report(report, target_status)

        if target_status == StatusChoices.COMPLETED:
            await sync_to_async(
                lambda: TripResult.objects.update_or_create(trip=trip, defaults={"result_info": report_entry})
            )()

        if trip.description:
            trip.description += f"\n\n{report_entry}"
        else:
            trip.description = report_entry

        trip.status = target_status
        await sync_to_async(trip.save)()

        if target_status == StatusChoices.ON_HOLD:
            response_text = (
                f"⏸ <b>Поездка {trip.task_number} переведена на удержание.</b>\n"
                "Причина сохранена."
            )
        else:
            response_text = (
                f"✅ <b>Поездка {trip.task_number} успешно завершена!</b>\n"
                "Отчет сохранен."
            )

        await message.answer(response_text, reply_markup=get_main_menu(), parse_mode="HTML")
    else:
        await message.answer("❌ Ошибка: поездка не найдена.")

    await state.clear()
