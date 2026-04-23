#!/usr/bin/env python3
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryFile, mkdtemp

import httpx
import pytest

from ant31box.client.filedl import DownloadClient, FileInfo
from ant31box.config import S3ConfigSchema


@pytest.mark.asyncio
async def test_filedl_http_temp(httpx_mock):
    path = "http://example.com/test.pdf"
    httpx_mock.add_response(
        url=path,
        status_code=200,
        content=b"test",
    )
    client = DownloadClient()
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
async def test_filedl_http_file(httpx_mock):
    path = "http://example.com/test.pdf"
    httpx_mock.add_response(
        url=path,
        status_code=200,
        content=b"test",
    )
    client = DownloadClient()
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
async def test_filedl_http_todir_file(httpx_mock):
    path = "http://example.com/test.pdf"
    httpx_mock.add_response(
        url=path,
        status_code=200,
        content=b"test",
    )
    dir = mkdtemp()
    client = DownloadClient()
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
async def test_filedl_http_todir(httpx_mock):
    path = "http://example.com/test.pdf"
    httpx_mock.add_response(
        url=path,
        status_code=200,
        content=b"test",
    )
    dir = mkdtemp()
    client = DownloadClient()

    resp = await client.download(source=path, dest_dir=dir)
    assert isinstance(resp, FileInfo)
    assert resp.filename == "test.pdf"
    assert resp.source == path
    assert resp.path == Path(dir).joinpath(resp.filename)
    assert resp.content is None
    with open(str(resp.path), "rb") as f:
        assert f.read() == b"test"


@pytest.mark.asyncio
async def test_filedl_404(httpx_mock):
    path = "https://example.com/test.pdf2"
    httpx_mock.add_response(
        url=path,
        status_code=404,
        content=b"",
    )
    client = DownloadClient()
    with TemporaryFile() as tmp, pytest.raises(httpx.HTTPStatusError) as excinfo:
        await client.download(source=path, output=tmp)
    assert excinfo.value.response.status_code == 404


@pytest.mark.asyncio
async def test_filedl_https_temp(httpx_mock):
    path = "https://example.com/test.pdf"
    httpx_mock.add_response(
        url=path,
        status_code=200,
        content=b"test",
    )
    client = DownloadClient()

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
    client = DownloadClient()
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
    client = DownloadClient()
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
async def test_filedl_file_scheme_file_s3(aioboto3_s3_client):
    config = S3ConfigSchema(
        secret_key="a", access_key="a", region="us-east-1", endpoint=aioboto3_s3_client.meta.endpoint_url
    )
    client = DownloadClient(s3_config=config)

    await aioboto3_s3_client.create_bucket(Bucket=client.s3.bucket)

    dir = mkdtemp()
    with NamedTemporaryFile() as tmp:
        tmp.write(b"test")
        tmp.seek(0)
        dest = "toto/test.pdf"
        await client.s3.upload_file_async(filepath=tmp.name, dest=dest)
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
async def test_filedl_file_scheme_output_s3(aioboto3_s3_client):
    config = S3ConfigSchema(
        secret_key="a", access_key="a", region="us-east-1", endpoint=aioboto3_s3_client.meta.endpoint_url
    )
    client = DownloadClient(s3_config=config)
    await aioboto3_s3_client.create_bucket(Bucket=client.s3.bucket)

    with NamedTemporaryFile() as tmp:
        tmp.write(b"test")
        tmp.seek(0)
        dest = "toto/test.pdf"
        await client.s3.upload_file_async(filepath=tmp.name, dest=dest)

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
