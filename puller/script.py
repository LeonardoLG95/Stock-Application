import asyncio

from puller import Puller


async def start_puller():
    # print('Waiting security time...')
    # await asyncio.sleep(61)
    # print('Starting service!')
    puller = Puller()
    await puller.start()

    # await puller.get_and_persist_info_for_all_symbols()

    await puller.get_and_persist_price_for_all_symbols('D')
    # await puller.get_and_persist_price_for_all_symbols('W')
    # await puller.get_and_persist_price_for_all_symbols('M')

    await puller.close()

asyncio.run(start_puller())
