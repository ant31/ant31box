import logging
from io import IOBase
from pathlib import Path
from typing import Tuple
from urllib.parse import urlparse

import boto3
from botocore.client import Config
from pydantic import BaseModel, Field

from ant31box.config import S3ConfigSchema

logger: logging.Logger = logging.getLogger(__name__)


class S3Dest(BaseModel):
    bucket: str = Field(...)
    path: str = Field(...)
    url: str = Field(default="")
    region: str = Field(default="")


class S3URL:
    def __init__(self, url: str = "", bucket: str = "", key: str = ""):
        self.parse_url(url)
        if bucket:
            self.bucket = bucket
        if key:
            self.key = key

    def to_dict(self):
        return {
            "bucket": self.bucket,
            "key": self.key,
            "url": self.url,
        }

    @property
    def url(self):
        return f"s3://{self.bucket}/{self.key}"

    def parse_url(self, value: str):
        if not value:
            return
        parsed = urlparse(value, allow_fragments=False)
        if parsed.scheme != "s3":
            raise ValueError(f"Invalid URL scheme {parsed.scheme}, must be 's3'")
        self.bucket = parsed.netloc
        self.key = parsed.path.lstrip("/")

    @property
    def filename(self) -> str:
        return Path(self.key).name


class S3Client:
    @staticmethod
    def _boto_args(options: S3ConfigSchema):
        kwargs: dict = {}
        if options.endpoint:
            kwargs["endpoint_url"] = options.endpoint
        if options.region:
            kwargs["region_name"] = options.region
        kwargs["aws_access_key_id"] = options.access_key
        kwargs["aws_secret_access_key"] = options.secret_key
        kwargs["config"] = Config(signature_version="s3v4")
        return kwargs

    def __init__(self, options: S3ConfigSchema, bucket: str = "", prefix: str = ""):
        kwargs: dict = self._boto_args(options)
        self.options = options
        self.client = boto3.resource("s3", **kwargs)
        if not bucket:
            bucket = options.bucket
        if not prefix:
            prefix = options.prefix
        self.bucket: str = bucket
        self.prefix: str = prefix

    def buildpath(self, filename: str, dest: str = ""):
        if not dest:
            dest = Path(filename).name
        return f"{self.prefix}{dest}"

    def upload_file(self, filepath: str | IOBase, dest: str = "") -> S3Dest:
        if isinstance(filepath, str):
            path = self.buildpath(filepath, dest)
            self.client.Bucket(self.bucket).upload_file(filepath, path)
        else:
            path = dest
            self.client.Bucket(self.bucket).upload_fileobj(filepath, path)

        return S3Dest(
            bucket=self.bucket, path=path, url=S3URL(bucket=self.bucket, key=path).url, region=self.options.region
        )

    def s3url(self, path: str, strip: bool = True) -> S3URL:
        if strip:
            path = path.lstrip("/")
        return S3URL(bucket=self.bucket, key=path)

    def download_file(self, s3url: S3URL, dest: str | Path | IOBase) -> str | IOBase:
        print(f"download uri='{s3url.url}'", f"dest='{dest}'")
        if isinstance(dest, (str, Path)):
            self.client.Bucket(s3url.bucket).download_file(s3url.key, str(dest))
        else:
            self.client.Bucket(s3url.bucket).download_fileobj(s3url.key, dest)
        return dest

    def copy_s3_to_s3(
        self,
        src_bucket: str,
        src_path: str,
        dest_bucket: str,
        dest_prefix: str = "",
        name_only: bool = False,
    ) -> Tuple[S3Dest, S3Dest]:
        copy_source = {
            "Bucket": src_bucket,
            "Key": src_path,
        }

        if not name_only:
            dest_path = f"{dest_prefix}{src_path}"
        else:
            dest_path = f"{dest_prefix}{Path(src_path).name}"

        self.client.meta.client.copy(copy_source, dest_bucket, dest_path)

        return (
            S3Dest(
                bucket=src_bucket,
                path=src_path,
                region=self.options.region,
                url=S3URL(bucket=src_bucket, key=src_path).url,
            ),
            S3Dest(
                bucket=dest_bucket,
                path=dest_path,
                region=self.options.region,
                url=S3URL(bucket=dest_bucket, key=dest_path).url,
            ),
        )
