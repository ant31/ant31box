# pylint: disable=no-name-in-module
# pylint: disable=too-few-public-methods
import logging

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ant31box.version import VERSION

router = APIRouter()

logger = logging.getLogger(__name__)


class VersionResp(BaseModel):
    version: str = Field(...)


@router.get("/", tags=["info"])
async def index():
    return await version()


@router.get("/version", tags=["info"], response_model=VersionResp)
async def version() -> VersionResp:
    return VersionResp(version=VERSION.app_version)
