import logging
from io import IOBase
from pathlib import Path
from typing import BinaryIO

import aioboto3
from botocore.client import Config

from ant31box.config import S3ConfigSchema
from ant31box.models import S3URL, S3Dest

logger: logging.Logger = logging.getLogger(__name__)


class S3Client:
    def __init__(self, options: S3ConfigSchema, bucket: str = "", prefix: str = ""):
        self.options = options
        self.session = aioboto3.Session(**self._boto_session_args(options))
        if not bucket:
            bucket = options.bucket
        if not prefix:
            prefix = options.prefix
        self.bucket: str = bucket
        self.prefix: str = prefix

    @staticmethod
    def _boto_session_args(options: S3ConfigSchema):
        kwargs: dict = {}
        if options.region:
            kwargs["region_name"] = options.region
        if options.access_key:
            kwargs["aws_access_key_id"] = options.access_key
        if options.secret_key:
            kwargs["aws_secret_access_key"] = options.secret_key
        return kwargs

    @staticmethod
    def _boto_client_args(options: S3ConfigSchema):
        kwargs: dict = {}
        if options.endpoint:
            kwargs["endpoint_url"] = options.endpoint
        kwargs["config"] = Config(signature_version="s3v4")
        return kwargs

    def buildpath(self, filename: str, dest: str = ""):
        if not dest:
            dest = Path(filename).name
        return f"{self.prefix}{dest}"

    async def upload_file(self, filepath: str | IOBase | BinaryIO, dest: str = "") -> S3Dest:
        path = dest if isinstance(filepath, (IOBase, BinaryIO)) else self.buildpath(filepath, dest)
        logger.info("upload s3 bucket='%s' file='%s' dest='%s'", self.bucket, filepath, path)

        async with self.session.resource("s3", **self._boto_client_args(self.options)) as s3:
            bucket = await s3.Bucket(self.bucket)
            if isinstance(filepath, str):
                await bucket.upload_file(filepath, path)
            else:
                await bucket.upload_fileobj(filepath, path)

        return S3URL(bucket=self.bucket, key=path, region=self.options.region).to_model()

    def s3url(self, path: str, strip: bool = True) -> S3URL:
        if strip:
            path = path.lstrip("/")
        return S3URL(bucket=self.bucket, key=path)

    async def download_file(self, s3url: S3Dest, dest: str | Path | IOBase | BinaryIO) -> str | IOBase | BinaryIO:
        logger.info("download uri='%s', dest='%s'", s3url.url, dest)
        async with self.session.resource("s3", **self._boto_client_args(self.options)) as s3:
            bucket = await s3.Bucket(s3url.bucket)
            if isinstance(dest, str | Path):
                await bucket.download_file(s3url.key, str(dest))
            else:
                await bucket.download_fileobj(s3url.key, dest)
        return dest

    async def copy_s3_to_s3(
        self,
        *,
        src_bucket: str,
        src_path: str,
        dest_bucket: str,
        dest_prefix: str = "",
        name_only: bool = False,
    ) -> tuple[S3Dest, S3Dest]:
        copy_source = {
            "Bucket": src_bucket,
            "Key": src_path,
        }

        if not name_only:
            dest_path = f"{dest_prefix}{src_path}"
        else:
            dest_path = f"{dest_prefix}{Path(src_path).name}"

        async with self.session.client("s3", **self._boto_client_args(self.options)) as client:
            await client.copy(copy_source, dest_bucket, dest_path)

        return (
            S3URL(bucket=src_bucket, key=src_path, region=self.options.region).to_model(),
            S3URL(bucket=dest_bucket, key=dest_path, region=self.options.region).to_model(),
        )
