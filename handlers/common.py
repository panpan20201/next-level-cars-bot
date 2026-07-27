from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from states import CarCalculation
from keyboards import get_back_keyboard, get_currency_keyboard, get_confirmation_keyboard

router = Router()

@router.message(CommandStart())
@router.message(F.text == "➕ Добавить еще анкету")
@router.message(F.text == "🔄 Сбросить и начать заново")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Привет! Давай рассчитаем стоимость авто.\n\nВведите курс USDT к воне:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(CarCalculation.waiting_for_manual_rate)

@router.message(F.text == "⬅️ Назад")
async def process_back(message: types.Message, state: FSMContext):
    current = await state.get_state()
    if current == CarCalculation.waiting_for_price:
        await state.set_state(CarCalculation.waiting_for_manual_rate)
        await message.answer("Введите курс USDT к воне:", reply_markup=types.ReplyKeyboardRemove())
    elif current == CarCalculation.waiting_for_freight_currency:
        await state.set_state(CarCalculation.waiting_for_price)
        await message.answer("Введите цену машины:", reply_markup=get_back_keyboard())
    elif current == CarCalculation.waiting_for_freight:
        await state.set_state(CarCalculation.waiting_for_freight_currency)
        await message.answer("Выберите валюту:", reply_markup=get_currency_keyboard())
    elif current == CarCalculation.waiting_for_confirmation:
        d = await state.get_data()
        await state.set_state(CarCalculation.waiting_for_freight)
        await message.answer(f"Введите фрахт в {d.get('freight_currency', '$')}:", reply_markup=get_back_keyboard())
