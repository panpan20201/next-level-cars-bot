import math
import logging
from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from states import CarCalculation
from utils import parse_smart_number, format_number
from keyboards import get_back_keyboard, get_currency_keyboard, get_confirmation_keyboard, get_restart_keyboard
from config import CHANNEL_ID

router = Router()


@router.message(CarCalculation.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(car_name=message.text.strip())
    await message.answer("Введите цену машины:", reply_markup=get_back_keyboard())
    await state.set_state(CarCalculation.waiting_for_price)


@router.message(CarCalculation.waiting_for_price)
async def process_price(message: types.Message, state: FSMContext):
    p = parse_smart_number(message.text)
    if p is None or p <= 0:
        return await message.answer("Пожалуйста, введите корректное число для цены.")

    await state.update_data(price=int(round(p)))

    # Красиво форматируем введённую цену для подтверждения
    formatted_price = format_number(p)

    await message.answer(
        f"Принято! Цена машины: {formatted_price}\n\n"
        f"Введите VIN-номер:",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(CarCalculation.waiting_for_vin)


@router.message(CarCalculation.waiting_for_vin)
async def process_vin(message: types.Message, state: FSMContext):
    await state.update_data(vin=message.text.upper().strip())
    await message.answer("В какой валюте будет вводимый фрахт?", reply_markup=get_currency_keyboard())
    await state.set_state(CarCalculation.waiting_for_freight_currency)


@router.message(CarCalculation.waiting_for_freight_currency, F.text.in_({"KRW", "USDT"}))
async def process_freight_currency(message: types.Message, state: FSMContext):
    await state.update_data(freight_currency=message.text)
    await message.answer(f"Введите стоимость фрахта в {message.text}:", reply_markup=get_back_keyboard())
    await state.set_state(CarCalculation.waiting_for_freight)


@router.message(CarCalculation.waiting_for_freight)
async def process_freight(message: types.Message, state: FSMContext):
    f = parse_smart_number(message.text)
    if f is None or f < 0:
        return await message.answer("Пожалуйста, введите корректное число для стоимости фрахта.")

    await state.update_data(freight=f)

    # Достаем валюту из контекста, чтобы красиво отобразить сумму
    d = await state.get_data()
    currency = d.get('freight_currency', 'USDT')
    formatted_freight = format_number(f)

    await message.answer(
        f"Принято! Стоимость фрахта: {formatted_freight} {currency}\n\n"
        f"Теперь введите курс USDT к воне вручную:",
        reply_markup=get_back_keyboard()
    )
    await state.set_state(CarCalculation.waiting_for_manual_rate)


@router.message(CarCalculation.waiting_for_manual_rate)
async def process_manual_rate(message: types.Message, state: FSMContext):
    rate = parse_smart_number(message.text)
    if not rate or rate <= 0:
        return await message.answer("Пожалуйста, введите корректное число для курса.")

    await state.update_data(manual_rate=rate)
    d = await state.get_data()

    # Расчеты
    nds = d['price'] * 0.09
    partners = nds * 0.40
    to_pay = d['price'] - partners

    if d['freight_currency'] == "KRW":
        freight_in_usdt = d['freight'] / rate
        freight_display = f"{format_number(d['freight'])} KRW"
    else:
        freight_in_usdt = d['freight']
        freight_display = f"{format_number(d['freight'])} USDT"

    usdt_total = math.ceil((to_pay / rate) + freight_in_usdt)

    report = (
        f"Автомобиль: {d['car_name']}\n"
        f"VIN: {d['vin']}\n"
        f"Цена: {format_number(d['price'])}\n"
        f"НДС: {format_number(nds)}\n"
        f"Партнерам: {format_number(partners)}\n"
        f"К оплате: {format_number(to_pay)}\n\n"
        f"Курс: {format_number(rate)}\n"
        f"Фрахт: {freight_display}\n\n"
        f"USDT: {format_number(usdt_total)}"
    )

    await state.update_data(report_text=report)

    # После ввода курса выводится сразу подтверждение курса и итоговый отчет
    await message.answer(f"Принято! Курс USDT к воне: {format_number(rate)}")
    await message.answer("Проверьте правильность заполнения анкеты:")
    await message.answer(report)
    await message.answer("Все верно? Подтвердите отправку анкеты в канал:", reply_markup=get_confirmation_keyboard())
    await state.set_state(CarCalculation.waiting_for_confirmation)


@router.message(CarCalculation.waiting_for_confirmation, F.text == "✅ Подтвердить и отправить")
async def process_confirmation(message: types.Message, state: FSMContext, bot: Bot):
    d = await state.get_data()
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=d['report_text'])
        await message.answer("Анкета успешно подтверждена и отправлена в канал!", reply_markup=get_restart_keyboard())
        await state.clear()
    except Exception as e:
        logging.error(f"Ошибка при отправке в канал: {e}")
        await message.answer("❌ Не удалось отправить анкету в канал. Проверьте права бота.")