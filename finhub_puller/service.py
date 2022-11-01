from migration_handler import migration
from puller import Puller
from datetime import datetime

from math import inf
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from drivers.timescale.api_driver import TimescaleDriver

from endpoints import END_POINT
from utils.logger import Logger

# Start migration
# migration()

APP = FastAPI()

# To allow React app connect to this app
APP.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LOGGER = Logger("API")
DB = TimescaleDriver(LOGGER)


@APP.post(END_POINT["start"])
async def start_puller():
    puller = Puller()
    await puller.start()
    puller.pull_tasks()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"response": "Puller finished successfully"},
    )


@APP.get(END_POINT["symbols"])
async def get_symbols() -> JSONResponse:
    stocks_list = await DB.select_stocks()
    if stocks_list is None:
        raise HTTPException(status_code=404, detail={"response": "Query not found"})

    LOGGER.info("List of symbols retrieved")

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"response": stocks_list}
    )


@APP.post(END_POINT["symbol_prices"])
async def get_symbol_data(request: Request) -> JSONResponse:
    request = await request.json()

    symbol = request.get("symbol")

    start_operation = request.get("start_operation")
    start_operation = datetime.strptime(start_operation, "%Y-%m-%dT%H:%M:%S.%fZ")

    end_operation = request.get("end_operation")
    if end_operation is not None:
        end_operation = datetime.strptime(end_operation, "%Y-%m-%dT%H:%M:%S.%fZ")

    resolution = request.get("resolution")

    prices = await DB.select_symbol_prices(
        symbol, start_operation, end_operation, resolution
    )
    if prices is None:
        raise HTTPException(status_code=404, detail={"response": "Query not found"})

    LOGGER.info(f"Prices for symbol {symbol} on resolution {resolution} retrieved")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"response": prices if len(prices) > 0 else None},
    )
