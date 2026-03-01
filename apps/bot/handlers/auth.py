from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from asgiref.sync import sync_to_async
from apps.accounts.models import User
from apps.bot.keyboards.main import get_main_menu, get_auth_kb

router = Router()

class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_psn = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    user = await sync_to_async(lambda: User.objects.filter(telegram_id=str(message.from_user.id)).first())()
    
    if user:
        await message.answer(
            f"🌟 <b>Добро пожаловать обратно, {user.fullname}!</b>\n\n"
            "Вы успешно авторизованы в системе TCMT Service. Воспользуйтесь меню для управления задачами.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "👋 <b>Здравствуйте!</b>\n\n"
            "Для работы с системой TCMT Service необходимо пройти регистрацию.\n\n"
            "Пожалуйста, нажмите кнопку ниже, чтобы начать.",
            reply_markup=get_auth_kb(),
            parse_mode="HTML"
        )

@router.message(F.text == "🚀 Начать регистрацию")
async def start_registration(message: Message, state: FSMContext):
    await state.set_state(RegistrationStates.waiting_for_name)
    await message.answer(
        "📝 Пожалуйста, введите ваше <b>ФИО</b> точно так, как оно указано в системе (например: <i>Иванов Иван Иванович</i>).",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )

@router.message(RegistrationStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(fullname=message.text.strip())
    await state.set_state(RegistrationStates.waiting_for_psn)
    await message.answer(
        "🆔 Теперь введите <b>Серию и Номер паспорта (PSN)</b> (например: <i>AA1234567</i>).",
        parse_mode="HTML"
    )

@router.message(RegistrationStates.waiting_for_psn)
async def process_psn(message: Message, state: FSMContext):
    data = await state.get_data()
    fullname = data['fullname']
    psn = message.text.strip()
    
    user = await sync_to_async(
        lambda: User.objects.filter(fullname__iexact=fullname, psn=psn).first()
    )()
    
    if user:
        if user.telegram_id and user.telegram_id != str(message.from_user.id):
            await message.answer(
                "❌ Этот аккаунт уже привязан к другому пользователю Telegram. "
                "Обратитесь к администратору."
            )
            await state.clear()
            return
        
        user.telegram_id = str(message.from_user.id)
        await sync_to_async(user.save)()
        await message.answer(
            f"✅ <b>Авторизация успешна!</b>\n\n"
            f"Ваш профиль <b>{user.fullname}</b> подтвержден.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
    else:
        # Автоматическое создание пользователя, если он не найден
        new_user = await sync_to_async(
            lambda: User.objects.create(
                fullname=fullname,
                psn=psn,
                login=f"tg_{message.from_user.id}",
                telegram_id=str(message.from_user.id)
            )
        )()
        await message.answer(
            f"🆕 <b>Вы зарегистрированы в системе!</b>\n\n"
            f"Создан новый профиль: <b>{new_user.fullname}</b>.\n"
            f"Теперь вы можете полноценно пользоваться ботом.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
    
    await state.clear()

@router.message(F.text == "👤 Профиль")
async def show_profile(message: Message):
    user = await sync_to_async(lambda: User.objects.filter(telegram_id=str(message.from_user.id)).first())()
    if user:
        text = (
            f"👤 <b>Ваш Профиль</b>\n\n"
            f"▫️ <b>ФИО:</b> {user.fullname}\n"
            f"▫️ <b>PSN:</b> {user.psn}\n"
            f"▫️ <b>ID:</b> {user.id}\n"
        )
        await message.answer(text, parse_mode="HTML")
    else:
        await message.answer("Пожалуйста, сначала зарегистрируйтесь.")
