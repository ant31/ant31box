# pylint: disable=no-name-in-module
# pylint: disable=too-few-public-methods
import asyncio
import logging

from fastapi import APIRouter

from ant31box.server.exception import Forbidden

router = APIRouter()

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/error", tags=["debug"])
async def gen_error():
    raise Forbidden("test")


@router.get("/error_uncatched", tags=["debug"])
async def gen_error_uncatch():
    raise Exception()


@router.get("/slow", tags=["debug"])
async def slow_req():
    await asyncio.sleep(5)
    return {"ok": 200}
