#!/usr/bin/env python3
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from ant31box.config import S3ConfigSchema
from ant31box.models import S3URL
from ant31box.s3 import S3Client


def test_s3url():
    s = S3URL(url="s3://bucket/test/key.pdf")
    assert s.bucket == "bucket"
    assert s.key == "test/key.pdf"
    assert s.url == "s3://bucket/test/key.pdf"
    assert s.filename == "key.pdf"
    s.bucket = "bucket2"
    assert s.bucket == "bucket2"
    assert s.url == "s3://bucket2/test/key.pdf"

    s = S3URL(url="s3://bucket/key.pdf", bucket="bucket3", key="lala/lili/toto.pdf")
    assert s.bucket == "bucket3"
    assert s.key == "lala/lili/toto.pdf"
    assert s.url == "s3://bucket3/lala/lili/toto.pdf"
    assert s.filename == "toto.pdf"

    s = S3URL(bucket="bucket4", key="lala/lili.pdf")
    assert s.bucket == "bucket4"
    assert s.key == "lala/lili.pdf"
    assert s.url == "s3://bucket4/lala/lili.pdf"
    assert s.filename == "lili.pdf"


def test_s3url_raise_scheme():
    with pytest.raises(ValueError):
        S3URL(url="https://bucket/test/key.pdf")


def test_s3url_parse():
    client = S3Client(S3ConfigSchema(secret_key="a", access_key="a"))
    assert client.s3url("test/key.pdf").url == "s3://abucket/test/key.pdf"


@pytest.mark.asyncio
async def test_s3_upload_from_file(aioboto3_s3_client):
    config = S3ConfigSchema(
        secret_key="a", access_key="a", region="us-east-1", endpoint=aioboto3_s3_client.meta.endpoint_url
    )
    client = S3Client(config)
    await aioboto3_s3_client.create_bucket(Bucket=client.bucket)

    with NamedTemporaryFile() as tmp:
        tmp.write(b"test")
        tmp.seek(0)
        dest = "toto/test.pdf"
        # from filepath
        a = await client.upload_file_async(filepath=tmp.name, dest=dest)
        assert a.url == f"s3://{client.bucket}/{dest}"


@pytest.mark.asyncio
async def test_s3_upload_from_file_nodest(aioboto3_s3_client):
    config = S3ConfigSchema(
        prefix="titi/",
        secret_key="a",
        access_key="a",
        region="us-east-1",
        endpoint=aioboto3_s3_client.meta.endpoint_url,
    )
    client = S3Client(config)
    await aioboto3_s3_client.create_bucket(Bucket=client.bucket)

    with NamedTemporaryFile() as tmp:
        tmp.write(b"test")
        tmp.seek(0)
        # from filepath
        a = await client.upload_file_async(filepath=tmp.name)
        assert a.url == f"s3://{client.bucket}/titi/{Path(tmp.name).name}"


@pytest.mark.asyncio
async def test_s3_download_to_file(aioboto3_s3_client):
    config = S3ConfigSchema(
        prefix="titi/",
        secret_key="a",
        access_key="a",
        region="us-east-1",
        endpoint=aioboto3_s3_client.meta.endpoint_url,
    )
    client = S3Client(config)
    await aioboto3_s3_client.create_bucket(Bucket=client.bucket)

    with NamedTemporaryFile() as tmp:
        tmp.write(b"test")
        tmp.seek(0)
        # from filepath
        a = await client.upload_file_async(filepath=tmp.name)
        assert a.url == f"s3://{client.bucket}/titi/{Path(tmp.name).name}"
    with NamedTemporaryFile() as output:
        await client.download_file_async(s3url=S3URL(url=a.url).to_model(), dest=str(output.name))
        with open(output.name, "rb") as fname:
            assert fname.read() == b"test"
        await client.download_file_async(s3url=S3URL(url=a.url).to_model(), dest=output)
        output.seek(0)
        assert output.read() == b"test"


@pytest.mark.asyncio
async def test_s3_copy_s3_s3(aioboto3_s3_client):
    config = S3ConfigSchema(
        prefix="titi/",
        secret_key="a",
        access_key="a",
        region="us-east-1",
        endpoint=aioboto3_s3_client.meta.endpoint_url,
    )
    client = S3Client(config)
    bucket2 = "bucketcopy"

    await aioboto3_s3_client.create_bucket(Bucket=client.bucket)
    await aioboto3_s3_client.create_bucket(Bucket=bucket2)

    with NamedTemporaryFile() as tmp:
        tmp.write(b"test")
        tmp.seek(0)
        src = await client.upload_file_async(filepath=tmp.name)
        assert src.url == f"s3://{client.bucket}/titi/{Path(tmp.name).name}"
    res = await client.copy_s3_to_s3_async(
        src_bucket=src.bucket, src_path=src.key, dest_bucket=bucket2, dest_prefix="copy/"
    )
    assert res[0].url == f"s3://{client.bucket}/titi/{Path(tmp.name).name}"
    assert res[1].url == f"s3://{bucket2}/copy/titi/{Path(tmp.name).name}"
    res = await client.copy_s3_to_s3_async(
        src_bucket=src.bucket, src_path=src.key, dest_bucket=bucket2, dest_prefix="copy/", name_only=True
    )
    assert res[0].url == f"s3://{client.bucket}/titi/{Path(tmp.name).name}"
    assert res[1].url == f"s3://{bucket2}/copy/{Path(tmp.name).name}"
