import asyncio

from puller import Puller


async def start_puller():
    # print('Waiting security time...')
    # await asyncio.sleep(61)
    # print('Starting service!')
    puller = Puller()
    await puller.start()
    asyncio.create_task(puller.daily_task_data_from_all_symbols())
    asyncio.create_task(puller.weekly_task_data_from_all_symbols())
    asyncio.create_task(puller.monthly_task_data_from_all_symbols())
    asyncio.create_task(puller.rehydrate_symbols())
    await asyncio.gather(*asyncio.all_tasks())


asyncio.run(start_puller())
