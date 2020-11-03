from django.conf import settings
from tortoise import Tortoise


async def init():
    await Tortoise.init(
        db_url=settings.PG_URL,
        modules={
            'customer': ['apps.customer.tortoise_models'],
            'bot': ['apps.bot.tortoise_models'],
        }
    )


async def start_db_connection():
    await init()

