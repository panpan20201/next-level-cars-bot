from aiogram.fsm.state import State, StatesGroup

class CarCalculation(StatesGroup):
    waiting_for_manual_rate = State()
    waiting_for_price = State()
    waiting_for_freight_currency = State()
    waiting_for_freight = State()
    waiting_for_confirmation = State()