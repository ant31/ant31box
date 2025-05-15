import hashlib
import logging
from email.message import EmailMessage
from io import IOBase
from pathlib import Path
from typing import Literal
from urllib.parse import unquote, urlparse

import aiofiles
import aioshutil as shutil
from pydantic import BaseModel, ConfigDict, Field

from ant31box.client.base import BaseClient
from ant31box.config import S3ConfigSchema
from ant31box.s3 import S3URL, S3Client

# create a temporary directory using the context manager


logger: logging.Logger = logging.getLogger(__name__)


class FileInfo(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    filename: str = Field(default="")
    content: IOBase | None = Field(default=None)
    path: Path | str | None = Field(default=None)
    source: str | Path | None = Field(default=None)
    metadata: dict[str, str] | None = Field(default=None)


class DownloadClient(BaseClient):
    def __init__(self, s3_config: S3ConfigSchema | None = None) -> None:
        super().__init__(endpoint="", client_name="filedl")
        self.s3 = None
        if s3_config is not None:
            self.set_s3(s3_config)

    def set_s3(self, s3_config: S3ConfigSchema) -> None:
        self.s3 = S3Client(s3_config)

    def _gen_sha(self, content: bytes, source_path: str, dest_dir: str, filename: str) -> str:
        path = Path(source_path)
        hashsha = hashlib.sha256(content)
        suffix = path.suffix
        filename = hashsha.hexdigest() + suffix
        return str(Path(dest_dir).joinpath(filename))

    async def copy_local_file(
        self, source_path: str, dest_dir: str | Path = "", output: str | Path | IOBase = ""
    ) -> FileInfo:
        filename = Path(source_path).name
        # Write output
        # if output is a IOBase, write the content to it and return it
        if output and isinstance(output, IOBase):
            # Read input
            async with aiofiles.open(source_path, "rb") as fopen:
                output.write(await fopen.read())
                return FileInfo(content=output, filename=filename, source=source_path)

        # if output is a string, write the content to that file and return
        elif output and isinstance(output, Path | str):
            dest_path = output
        else:
            dest_path = Path(dest_dir).joinpath(filename)
        await shutil.copyfile(source_path, dest_path)
        return FileInfo(filename=filename, path=dest_path, source=source_path)

    def headers(
        self, content_type: Literal["json", "form"] | str | None = None, extra: dict[str, str] | None = None
    ) -> dict[str, str]:
        headers = {
            "Accept": "*/*",
        }
        if extra is not None:
            headers.update(extra)
        return super().headers(content_type=content_type, extra=headers)

    async def download_file(
        self, url: str, source_path: str, dest_dir: str | Path = "", output: str | Path | IOBase = ""
    ) -> FileInfo:
        resp = await self.session.get(url, headers=self.headers())
        resp.raise_for_status()

        filename: str = ""

        content_disposition = resp.headers.get("Content-Disposition")
        if content_disposition:
            msg = EmailMessage()
            msg["Content-Disposition"] = content_disposition
            _, params = msg.get_content_type(), msg["Content-Disposition"].params
            filename = params.get("filename", "")
        if not filename:
            filename = unquote(Path(source_path).name)

        content = await resp.content.read()

        if output and isinstance(output, IOBase):
            output.write(content)
            fd = FileInfo(content=output, filename=filename, source=url)
            return fd
        if output and isinstance(output, Path | str):
            dest_path = output
        else:
            dest_path = Path(dest_dir).joinpath(filename)
        async with aiofiles.open(dest_path, "wb") as fopen:
            await fopen.write(content)
        fd = FileInfo(filename=filename, path=dest_path, source=url)
        return fd

    def download_s3(self, source: str, dest_dir: str | Path = "", output: str | Path | IOBase = "") -> FileInfo:
        s3url = S3URL(url=source)
        fd = FileInfo(source=source, filename=s3url.filename, metadata=s3url.to_dict())
        if self.s3 is None:
            raise AttributeError("S3 client is not set")
        if not output:
            output = Path(dest_dir).joinpath(s3url.filename)
        if output and hasattr(output, "write"):
            # write to file-like object
            self.s3.download_file(s3url=s3url.to_model(), dest=output)
            fd.content = output
        if output and isinstance(output, Path | str):
            # write to file on disk
            with open(str(output), "wb") as fileobj:
                self.s3.download_file(s3url=s3url.to_model(), dest=fileobj)
            fd.path = output
        return fd

    async def download(self, source: str, dest_dir: str | Path = "", output: str | Path | IOBase = "") -> FileInfo:
        """
        Determine the protocol to fetch the document:
        file://,
        http://,
        s3:// ...
        """
        parsedurl = urlparse(source)
        logger.info("download %s, %s", source, parsedurl.path)
        if parsedurl.scheme in ["file", ""]:
            return await self.copy_local_file(source_path=parsedurl.path, dest_dir=dest_dir, output=output)
        if parsedurl.scheme in ["http", "https"]:
            return await self.download_file(url=source, source_path=parsedurl.path, dest_dir=dest_dir, output=output)
        if parsedurl.scheme in ["s3"]:
            return self.download_s3(source=source, dest_dir=dest_dir, output=output)
        raise AttributeError(f"Unsupported file source: scheme={parsedurl.scheme} - path={parsedurl.path}")
