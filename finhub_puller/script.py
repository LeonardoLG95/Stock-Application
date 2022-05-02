import asyncio

from puller import Puller


async def start_puller():
    finhub_puller = Puller()
    
    await finhub_puller.start()

    await finhub_puller.get_and_persist_info_for_all_symbols()

    await finhub_puller.get_and_persist_price_for_all_symbols('D')
    await finhub_puller.get_and_persist_price_for_all_symbols('W')
    await finhub_puller.get_and_persist_price_for_all_symbols('M')

    await finhub_puller.close()

asyncio.run(start_puller())
