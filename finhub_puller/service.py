import asyncio

from migration_handler import alembic_migration
from puller import Puller

alembic_migration()


async def start_puller():
    puller = Puller()
    await puller.start()
    puller.pull_tasks()
    await asyncio.gather(*asyncio.all_tasks())


asyncio.run(start_puller())
