from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from asgiref.sync import sync_to_async

from apps.accounts.models import User
from apps.bot.keyboards.main import get_main_menu
from apps.core.choices import StatusChoices
from apps.tasks.models import Task

router = Router()


class TaskStates(StatesGroup):
    waiting_for_report = State()


def get_task_device_type_name(task: Task) -> str:
    return task.device_type.name if task.device_type else "Не указано"


def get_task_actions_kb(task_id, current_status):
    buttons = []

    if current_status != StatusChoices.PENDING:
        buttons.append(
            [InlineKeyboardButton(text="⏳ В работу", callback_data=f"task_status:{task_id}:{StatusChoices.PENDING}")]
        )

    if current_status != StatusChoices.ON_HOLD:
        buttons.append(
            [InlineKeyboardButton(text="⏸ На удержание", callback_data=f"task_status:{task_id}:{StatusChoices.ON_HOLD}")]
        )

    if current_status != StatusChoices.COMPLETED:
        buttons.append([InlineKeyboardButton(text="✅ Завершить", callback_data=f"task_complete:{task_id}")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text == "📋 Мои задачи")
async def list_user_tasks(message: Message):
    user = await sync_to_async(lambda: User.objects.filter(telegram_id=str(message.from_user.id)).first())()
    if not user:
        await message.answer("❌ Сначала зарегистрируйтесь.")
        return

    tasks = await sync_to_async(
        lambda: list(
            Task.objects.filter(responsible_persons=user)
            .exclude(status__in=[StatusChoices.COMPLETED, StatusChoices.CANCELED])
            .select_related("device_type")[:15]
        )
    )()

    if not tasks:
        await message.answer("🏝 <b>У вас нет активных задач!</b>", parse_mode="HTML")
        return

    text = "📋 <b>Ваши активные задачи:</b>\n"
    text += "────────────────────\n\n"
    for task in tasks:
        status_icon = "🆕" if task.status == StatusChoices.NEW else "⏳" if task.status == StatusChoices.PENDING else "⏸"
        text += (
            f"🆔 <b>№ {task.task_number}</b>\n"
            f"🩺 {get_task_device_type_name(task)}\n"
            f"🚦 {status_icon} {task.get_status_display()}\n"
            f"🔗 /task_{task.id}\n\n"
        )

    await message.answer(text, parse_mode="HTML")


@router.message(F.text.startswith("/task_"))
async def show_task_detail(message: Message):
    task_id = message.text.split("_")[1]
    user = await sync_to_async(lambda: User.objects.filter(telegram_id=str(message.from_user.id)).first())()

    task = await sync_to_async(
        lambda: Task.objects.filter(id=task_id, responsible_persons=user)
        .select_related("device_type", "hospital", "category")
        .first()
    )()

    if not task:
        await message.answer("❌ Задача не найдена или у вас нет к ней доступа.")
        return

    responsibles = await sync_to_async(lambda: ", ".join([u.fullname for u in task.responsible_persons.all()]))()
    hospital_name = task.hospital.name if task.hospital else "Не указана"

    text = (
        f"📋 <b>ЗАДАЧА № {task.task_number}</b>\n"
        "────────────────────\n\n"
        f"📂 <b>Категория:</b> {task.category.name if task.category else 'Не указана'}\n"
        f"📞 <b>Телефон:</b> {task.phone_number or 'Не указан'}\n"
        f"👥 <b>Ответственные:</b>\n└ {responsibles}\n\n"
        f"📍 <b>Локация:</b>\n└ {hospital_name}\n\n"
        f"🩺 <b>Оборудование:</b>\n└ {get_task_device_type_name(task)}\n\n"
        f"📝 <b>Описание проблемы:</b>\n{task.description}\n\n"
        f"📅 <b>Дата заявки:</b> {task.task_date or 'Не указана'}\n"
        f"🚦 <b>Текущий статус:</b> <u>{task.get_status_display()}</u>\n"
    )

    await message.answer(text, reply_markup=get_task_actions_kb(task.id, task.status), parse_mode="HTML")


@router.callback_query(F.data.startswith("task_status:"))
async def change_task_status(callback: CallbackQuery):
    _, task_id, new_status = callback.data.split(":")

    task = await sync_to_async(lambda: Task.objects.filter(id=task_id).first())()
    if task:
        task.status = new_status
        await sync_to_async(task.save)()

        await callback.answer("🔄 Статус обновлен!")
        base_text = callback.message.text.split("🚦")[0]
        new_text = base_text + f"🚦 <b>Текущий статус:</b> <u>{task.get_status_display()}</u>"

        await callback.message.edit_text(
            new_text,
            parse_mode="HTML",
            reply_markup=get_task_actions_kb(task.id, task.status),
        )
    else:
        await callback.answer("❌ Ошибка!")


@router.callback_query(F.data.startswith("task_complete:"))
async def start_task_completion(callback: CallbackQuery, state: FSMContext):
    task_id = callback.data.split(":")[1]
    await state.set_state(TaskStates.waiting_for_report)
    await state.update_data(task_id=task_id)

    await callback.message.answer(
        "📝 Пожалуйста, напишите краткий <b>отчет о проделанной работе</b> для закрытия заявки:",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(TaskStates.waiting_for_report)
async def process_task_report(message: Message, state: FSMContext):
    data = await state.get_data()
    task_id = data["task_id"]
    report = message.text.strip()

    task = await sync_to_async(lambda: Task.objects.filter(id=task_id).first())()
    if task:
        task.description += f"\n\n--- ОТЧЕТ ---\n{report}"
        task.status = StatusChoices.COMPLETED
        await sync_to_async(task.save)()

        await message.answer(
            f"✅ <b>Задача {task.task_number} успешно завершена!</b>\nОтчет сохранен.",
            reply_markup=get_main_menu(),
            parse_mode="HTML",
        )
    else:
        await message.answer("❌ Ошибка: задача не найдена.")

    await state.clear()
