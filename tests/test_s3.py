#!/usr/bin/env python3
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from moto import mock_aws

from ant31box.config import S3ConfigSchema
from ant31box.s3 import S3URL, S3Client


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
    client = S3Client(S3ConfigSchema())
    assert client.s3url("test/key.pdf").url == "s3://abucket/test/key.pdf"


async def test_s3_upload_from_file():
    client = S3Client(S3ConfigSchema())
    with mock_aws():
        with NamedTemporaryFile() as tmp:
            tmp.write(b"test")
            tmp.seek(0)
            dest = "toto/test.pdf"

            location = {"LocationConstraint": client.options.region}
            client.client.create_bucket(Bucket=client.bucket, CreateBucketConfiguration=location)
            # from filepath
            a = client.upload_file(filepath=tmp.name, dest=dest)
            assert a.url == f"s3://{client.bucket}/{dest}"


async def test_s3_upload_from_file_nodest():
    client = S3Client(S3ConfigSchema(prefix="titi/"))
    with mock_aws():
        with NamedTemporaryFile() as tmp:
            tmp.write(b"test")
            tmp.seek(0)
            location = {"LocationConstraint": client.options.region}
            client.client.create_bucket(Bucket=client.bucket, CreateBucketConfiguration=location)
            # from filepath
            a = client.upload_file(filepath=tmp.name)
            assert a.url == f"s3://{client.bucket}/titi/{Path(tmp.name).name}"


async def test_s3_download_to_file():
    client = S3Client(S3ConfigSchema(prefix="titi/"))
    with mock_aws():
        with NamedTemporaryFile() as tmp:
            tmp.write(b"test")
            tmp.seek(0)
            location = {"LocationConstraint": client.options.region}
            client.client.create_bucket(Bucket=client.bucket, CreateBucketConfiguration=location)
            # from filepath
            a = client.upload_file(filepath=tmp.name)
            assert a.url == f"s3://{client.bucket}/titi/{Path(tmp.name).name}"
        with NamedTemporaryFile() as output:
            client.download_file(s3url=S3URL(url=a.url), dest=str(output.name))
            with open(output.name, "rb") as fname:
                assert fname.read() == b"test"
            client.download_file(s3url=S3URL(url=a.url), dest=output)
            output.seek(0)
            assert output.read() == b"test"


async def test_s3_copy_s3_s3():
    client = S3Client(S3ConfigSchema(prefix="titi/"))
    with mock_aws():
        location = {"LocationConstraint": client.options.region}
        bucket2 = "bucketcopy"
        client.client.create_bucket(Bucket=client.bucket, CreateBucketConfiguration=location)
        client.client.create_bucket(Bucket=bucket2, CreateBucketConfiguration=location)
        with NamedTemporaryFile() as tmp:
            tmp.write(b"test")
            tmp.seek(0)
            src = client.upload_file(filepath=tmp.name)
            assert src.url == f"s3://{client.bucket}/titi/{Path(tmp.name).name}"
        res = client.copy_s3_to_s3(src_bucket=src.bucket, src_path=src.path, dest_bucket=bucket2, dest_prefix="copy/")
        assert res[0].url == f"s3://{client.bucket}/titi/{Path(tmp.name).name}"
        assert res[1].url == f"s3://{bucket2}/copy/titi/{Path(tmp.name).name}"
        res = client.copy_s3_to_s3(
            src_bucket=src.bucket, src_path=src.path, dest_bucket=bucket2, dest_prefix="copy/", name_only=True
        )
        assert res[0].url == f"s3://{client.bucket}/titi/{Path(tmp.name).name}"
        assert res[1].url == f"s3://{bucket2}/copy/{Path(tmp.name).name}"
