from json import dumps, loads
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from drivers.timescale.api_driver import TimescaleDriver

from api_src.constants import END_POINT
from utils.logger import Logger


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


@APP.get(END_POINT["symbols"])
async def get_symbols() -> JSONResponse:
    symbol_list = await DB.select_symbols()

    LOGGER.info("List of symbols retrieved")

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"response": symbol_list}
    )
    # if state is None:
    #     raise HTTPException(status_code=404, detail=ERR_ID_NOT_FOUND)

    # return JSONResponse(status_code=status.HTTP_200_OK, content=state)
