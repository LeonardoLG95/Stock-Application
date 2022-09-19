"""
This module retrieve information from the db to expose through an API
"""

from drivers.timescale.base_driver import BaseDriver
from sqlalchemy.future import select
from alembic_files.alembic.models import Symbol
from sqlalchemy.exc import NoResultFound


class TimescaleDriver(BaseDriver):
    def __init__(self, log):
        super().__init__(log=log)

    async def select_symbols(self):
        engine, session = await self._create_session()

        async with session() as session:
            symbol_list = await session.execute(select(Symbol))

            try:
                symbol_list = [symbol.symbol for symbol in symbol_list.scalars()]
            except NoResultFound:
                ...

            await session.commit()
        await self._close(session, engine)

        return symbol_list
