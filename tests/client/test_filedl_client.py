#!/usr/bin/env python3
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryFile, mkdtemp

import aiohttp
import pytest
from moto import mock_aws

from ant31box.client.filedl import FileInfo
from ant31box.clients import filedl_client
from ant31box.config import S3ConfigSchema


@pytest.mark.asyncio
async def test_filedl_http_temp(aioresponses):
    path = "http://example.com/test.pdf"
    aioresponses.get(
        path,
        status=200,
        body=b"test",
    )
    client = filedl_client()
    with TemporaryFile() as tmp:
        resp = await client.download(source=path, output=tmp)
        tmp.seek(0)
        assert isinstance(resp, FileInfo)
        assert tmp.read() == b"test"
        assert resp.filename == "test.pdf"
        assert resp.source == path
        assert resp.path is None
        assert resp.content is tmp


@pytest.mark.asyncio
async def test_filedl_http_file(aioresponses):
    path = "http://example.com/test.pdf"
    aioresponses.get(
        path,
        status=200,
        body=b"test",
    )
    client = filedl_client()
    with NamedTemporaryFile() as tmp:
        resp = await client.download(source=path, output=tmp.name)
        tmp.seek(0)
        assert isinstance(resp, FileInfo)
        assert tmp.read() == b"test"
        assert resp.filename == "test.pdf"
        assert resp.source == path
        assert resp.path == tmp.name
        assert resp.content is None


@pytest.mark.asyncio
async def test_filedl_http_todir_file(aioresponses):
    path = "http://example.com/test.pdf"
    aioresponses.get(
        path,
        status=200,
        body=b"test",
    )
    dir = mkdtemp()
    client = filedl_client()
    with NamedTemporaryFile() as tmp:
        resp = await client.download(source=path, dest_dir=dir, output=tmp.name)
        tmp.seek(0)
        assert isinstance(resp, FileInfo)
        assert tmp.read() == b"test"
        assert resp.filename == "test.pdf"
        assert resp.source == path
        assert resp.path == str(Path(dir).joinpath(tmp.name))
        assert resp.content is None


@pytest.mark.asyncio
async def test_filedl_http_todir(aioresponses):
    path = "http://example.com/test.pdf"
    aioresponses.get(
        path,
        status=200,
        body=b"test",
    )
    dir = mkdtemp()
    client = filedl_client()

    resp = await client.download(source=path, dest_dir=dir)
    assert isinstance(resp, FileInfo)
    assert resp.filename == "test.pdf"
    assert resp.source == path
    assert resp.path == Path(dir).joinpath(resp.filename)
    assert resp.content is None
    with open(str(resp.path), "rb") as f:
        assert f.read() == b"test"


@pytest.mark.asyncio
async def test_filedl_404(aioresponses):
    path = "https://example.com/test.pdf2"
    aioresponses.get(
        path,
        status=404,
        body=b"",
    )
    client = filedl_client()
    with TemporaryFile() as tmp, pytest.raises(aiohttp.ClientResponseError) as excinfo:
        await client.download(source=path, output=tmp)
    assert excinfo.value.status == 404


@pytest.mark.asyncio
async def test_filedl_https_temp(aioresponses):
    path = "https://example.com/test.pdf"
    aioresponses.get(
        path,
        status=200,
        body=b"test",
    )
    client = filedl_client()

    with TemporaryFile() as tmp:
        resp = await client.download(source=path, output=tmp)
        tmp.seek(0)
        assert isinstance(resp, FileInfo)
        assert tmp.read() == b"test"
        assert resp.filename == "test.pdf"
        assert resp.source == path
        assert resp.path is None
        assert resp.content is tmp


@pytest.mark.asyncio
async def test_filedl_file():
    client = filedl_client()
    dir = mkdtemp()
    with NamedTemporaryFile() as tmp:
        tmp.write(b"test")
        tmp.seek(0)
        path = Path(tmp.name)
        resp = await client.download(source=str(path), dest_dir=dir)
        assert isinstance(resp, FileInfo)
        assert tmp.read() == b"test"
        assert resp.filename == str(path.name)
        assert resp.source == str(path)
        assert resp.path == Path(dir).joinpath(path.name)
        assert resp.content is None


@pytest.mark.asyncio
async def test_filedl_file_scheme():
    client = filedl_client()
    dir = mkdtemp()
    with NamedTemporaryFile() as tmp:
        tmp.write(b"test")
        tmp.seek(0)
        path = Path(tmp.name)
        resp = await client.download(source=f"file://{path}", dest_dir=dir)
        assert isinstance(resp, FileInfo)
        assert tmp.read() == b"test"
        assert resp.filename == str(path.name)
        assert resp.source == str(path)
        assert resp.path == Path(dir).joinpath(path.name)
        assert resp.content is None


@pytest.mark.asyncio
async def test_filedl_file_scheme_file_s3():
    client = filedl_client()
    client.set_s3(S3ConfigSchema(secret_key="a", access_key="a"))

    dir = mkdtemp()
    with NamedTemporaryFile() as tmp:
        tmp.write(b"test")
        tmp.seek(0)
        dest = "toto/test.pdf"
        with mock_aws():
            location = {"LocationConstraint": client.s3.options.region}
            client.s3.client.create_bucket(Bucket=client.s3.bucket, CreateBucketConfiguration=location)
            client.s3.upload_file(filepath=tmp, dest=dest)
            uri = f"s3://{client.s3.bucket}/{dest}"
            resp = await client.download(source=uri, dest_dir=dir)
        assert isinstance(resp, FileInfo)
        with open(str(resp.path), "rb") as f:
            assert f.read() == b"test"

        assert resp.filename == "test.pdf"
        assert resp.source == uri
        assert str(resp.path) == str(Path(dir).joinpath(resp.filename))
        assert resp.content is None


@pytest.mark.asyncio
async def test_filedl_file_scheme_output_s3():
    client = filedl_client()
    client.set_s3(S3ConfigSchema(secret_key="a", access_key="a"))
    with mock_aws():
        with NamedTemporaryFile() as tmp:
            tmp.write(b"test")
            tmp.seek(0)
            dest = "toto/test.pdf"

            location = {"LocationConstraint": client.s3.options.region}
            client.s3.client.create_bucket(Bucket=client.s3.bucket, CreateBucketConfiguration=location)
            client.s3.upload_file(filepath=tmp, dest=dest)
        with NamedTemporaryFile() as output:
            uri = f"s3://{client.s3.bucket}/{dest}"
            resp = await client.download(source=uri, dest_dir="", output=output)
            print(resp.model_dump())
            assert isinstance(resp, FileInfo)
            output.seek(0)
            assert output.read() == b"test"
            assert resp.filename == "test.pdf"
            assert resp.source == uri
            assert resp.path is None
            assert resp.content is not None
