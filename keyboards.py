from aiogram import types

def get_back_keyboard():
    return types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="⬅️ Назад")]], resize_keyboard=True)

def get_currency_keyboard():
    return types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="$"), types.KeyboardButton(text="₩")], [types.KeyboardButton(text="⬅️ Назад")]], resize_keyboard=True)

def get_confirmation_keyboard():
    return types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="✅ Подтвердить и отправить")], [types.KeyboardButton(text="🔄 Сбросить и начать заново")], [types.KeyboardButton(text="⬅️ Назад")]], resize_keyboard=True)

def get_restart_keyboard():
    return types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="➕ Добавить еще анкету")]], resize_keyboard=True)