import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError

import config
from handlers import setup_routers

RECONNECT_MIN_DELAY = 10    # секунд перед первой повторной попыткой
RECONNECT_MAX_DELAY = 300   # потолок задержки между попытками (5 минут)
ALERT_AFTER_FAILURES = 3    # после скольких неудач подряд слать оповещение


async def send_alert(text: str):
    """
    Best-effort отправка оповещения администратору отдельной короткоживущей сессией.
    Если сама отправка не удалась (например, прокси совсем не работает) —
    просто логируем и не роняем основной цикл переподключения.
    """
    if not config.ADMIN_CHAT_ID:
        return
    session = AiohttpSession(proxy=config.SOCKS5_PROXY)
    try:
        alert_bot = Bot(token=config.BOT_TOKEN, session=session)
        await alert_bot.send_message(chat_id=config.ADMIN_CHAT_ID, text=text)
    except Exception as e:
        logging.error(f"Не удалось отправить оповещение админу: {e}")
    finally:
        await session.close()


async def run_bot():
    failures_in_a_row = 0
    was_down = False

    while True:
        session = AiohttpSession(proxy=config.SOCKS5_PROXY)
        try:
            bot = Bot(token=config.BOT_TOKEN, session=session)
            dp = Dispatcher()
            dp.include_router(setup_routers())

            await bot.delete_webhook(drop_pending_updates=True)
            logging.info("Бот запущен!")

            if was_down:
                await send_alert("✅ Бот снова в сети, соединение восстановлено.")
                was_down = False
            failures_in_a_row = 0

            await dp.start_polling(bot)
            # start_polling завершился без исключения (штатная остановка) — выходим из цикла
            break

        except (TelegramNetworkError, ConnectionError, OSError) as err:
            failures_in_a_row += 1
            was_down = True
            logging.error(f"Сбой соединения (попытка {failures_in_a_row}): {err}")

            if failures_in_a_row == ALERT_AFTER_FAILURES:
                await send_alert(
                    f"⚠️ Бот не может подключиться уже {failures_in_a_row} попыток подряд.\n"
                    f"Последняя ошибка: {err}"
                )

        except Exception as err:
            logging.critical(f"Критическая ошибка: {err}", exc_info=True)
            failures_in_a_row += 1
            was_down = True

        finally:
            await session.close()

        delay = min(RECONNECT_MIN_DELAY * (2 ** min(failures_in_a_row - 1, 5)), RECONNECT_MAX_DELAY)
        logging.info(f"Повторная попытка подключения через {delay} сек.")
        await asyncio.sleep(delay)


if __name__ == "__main__":
    asyncio.run(run_bot())
