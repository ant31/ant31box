import hashlib
import hmac
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field


class S3Dest(BaseModel):
    bucket: str = Field(...)
    key: str = Field(...)
    url: str = Field(default="")
    region: str = Field(default="")

    def to_s3url(self) -> "S3URL":
        return S3URL(url=self.url, bucket=self.bucket, key=self.key, region=self.region)


class S3URL:
    def __init__(self, url: str = "", bucket: str = "", key: str = "", region: str = ""):
        self.parse_url(url)
        if bucket:
            self.bucket = bucket
        if key:
            self.key = key
        self.region = region

    def to_dict(self):
        return {
            "bucket": self.bucket,
            "key": self.key,
            "url": self.url,
            "region": self.region,
        }

    def to_model(self) -> S3Dest:
        return S3Dest(bucket=self.bucket, key=self.key, url=self.url, region=self.region)

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


class Job(BaseModel):
    uuid: str = Field(...)
    name: str = Field(...)
    status: str | None = Field(default=None)
    result: dict[str, Any] = Field(default={})


class JobList(BaseModel):
    jobs: list[Job] = Field([])


class AsyncResponse(BaseModel):
    payload: JobList = Field(default=JobList(jobs=[]))
    signature: str | None = Field(default=None)
    _secret_key: bytes = b"NhqPtmfle3R5aNIP1e3uzjonClVN65XAbvqqM6A7H5fATj0j"

    def gen_signature(self):
        self.signature = hmac.new(self._secret_key, self.payload.model_dump_json().encode(), hashlib.sha256).hexdigest()
        return self.signature

    def check_signature(self):
        expect = hmac.new(self._secret_key, self.payload.model_dump_json().encode(), hashlib.sha256).hexdigest()
        return expect != self.signature
