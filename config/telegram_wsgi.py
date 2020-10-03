import asyncio

from aiogram.dispatcher.webhook import get_new_configured_app
from django.conf import settings

from apps.bot import bot, dispatcher
from apps.bot.middleware import AccessControl
from tortoise_config.models import start_db_connection

TELEGRAM_TOKEN = settings.TELEGRAM_TOKEN


async def on_startup(app):
    dispatcher.middleware.setup(AccessControl())
    await start_db_connection()
    await bot.set_webhook(f'{settings.WEBHOOK_URL}/telegram/{TELEGRAM_TOKEN}')


async def on_shutdown(app):
    await bot.delete_webhook()
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


async def web_app():
    from apps.bot import telegram_views
    from apps.customer import telegram_views
    app = get_new_configured_app(dispatcher=dispatcher, path=f'/telegram/{TELEGRAM_TOKEN}')
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app
