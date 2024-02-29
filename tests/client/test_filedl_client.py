#!/usr/bin/env python3
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryFile, mkdtemp

import aiohttp
import pytest

from ant31box.client.filedl import FileInfo
from ant31box.clients import filedl_client


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
    with TemporaryFile() as tmp:
        with pytest.raises(aiohttp.ClientResponseError) as excinfo:
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


# @pytest.mark.asyncio
# async def test_headers(mock_gh_token):
#     _ = mock_gh_token
#     client = GGithubClient()
#     headers = await client.headers()
#     assert headers["Authorization"] == "token valid-access-token"


# @pytest.mark.asyncio
# async def test_create_check_run(aioresponses, mock_gh_token):
#     _ = mock_gh_token
#     github_repo = "ant31/ffci"
#     path = f"https://api.github.com/repos/{github_repo}/check-runs"
#     aioresponses.post(
#         path,
#         status=200,
#         body=GithubCheckRun(
#             name="test",
#             head_sha="1234",
#             status="in_progress",
#             started_at=datetime.fromisoformat("2021-01-01T00:00:00Z"),
#             id=3,
#         ).model_dump_json(),
#     )
#     client = GGithubClient()
#     body = CreateGithubCheckRun(
#         name="test",
#         head_sha="1234",
#         status="in_progress",
#         started_at=datetime.fromisoformat("2021-01-01T00:00:00Z"),
#     )

#     resp = await client.create_check(github_repo=github_repo, check_body=body)
#     assert resp.name == "test"
#     assert resp.id == 3


# @pytest.mark.asyncio
# async def test_update_check_run(aioresponses, mock_gh_token):
#     _ = mock_gh_token
#     github_repo = "ant31/ffci"
#     path = f"https://api.github.com/repos/{github_repo}/check-runs/3"
#     aioresponses.patch(
#         path,
#         status=200,
#         body=GithubCheckRun(
#             name="test",
#             head_sha="1234",
#             status="in_progress",
#             started_at=datetime.fromisoformat("2021-01-01T00:00:00Z"),
#             id=3,
#         ).model_dump_json(),
#     )
#     client = GGithubClient()
#     body = UpdateGithubCheckRun(
#         name="test",
#         status="completed",
#         started_at=datetime.fromisoformat("2021-01-01T00:00:00Z"),
#     )

#     resp = await client.update_check_run(
#         github_repo=github_repo, check_body=body, check_id=3
#     )
#     assert resp.name == "test"
#     assert resp.id == 3


# @pytest.mark.asyncio
# async def test_get_ci_file(aioresponses, mock_gh_token):
#     _ = mock_gh_token
#     github_repo = "ant31/ffci"
#     ref = "1234"
#     path = (
#         f"https://api.github.com/repos/{github_repo}/contents/.gitlab-ci.yml?ref={ref}"
#     )
#     aioresponses.get(
#         path, status=200, payload={"content": "dGVzdA==", "encoding": "base64"}
#     )
#     client = GGithubClient()
#     resp = await client.get_ci_file(source_repo=github_repo, ref=ref)
#     assert resp == {"content": b"test", "file": ".gitlab-ci.yml"}


# @pytest.mark.asyncio
# async def test_get_ci_file_not_found(aioresponses, mock_gh_token):
#     _ = mock_gh_token
#     github_repo = "ant31/ffci"
#     ref = "1234"

#     path = (
#         f"https://api.github.com/repos/{github_repo}/contents/.gitlab-ci.yml?ref={ref}"
#     )
#     path2 = f"https://api.github.com/repos/{github_repo}/contents/.failfast-ci.jsonnet?ref={ref}"
#     aioresponses.get(path, status=404, payload={})
#     aioresponses.get(path2, status=500, payload={})
#     client = GGithubClient()
#     with pytest.raises(aiohttp.ClientResponseError) as excinfo:
#         await client.get_ci_file(source_repo=github_repo, ref=ref)
#         assert excinfo.value.status == 500
#     aioresponses.get(path, status=404, payload={})
#     aioresponses.get(path2, status=404, payload={})
#     with pytest.raises(aiohttp.ClientResponseError) as excinfo:
#         await client.get_ci_file(source_repo=github_repo, ref=ref)
#         assert excinfo.value.status == 404


# def test_jwt_token(mock_jwttoken):
#     client = GGithubClient()
#     token = client.jwt_token()
#     assert token == "mocked-token"


# async def test_close_session():
#     client = GGithubClient()
#     assert client.session.closed is False
#     await client.close()
#     assert client.session.closed
#     await GGithubClient.reinit()


# async def test_close_session_reinit():
#     await GGithubClient.reinit()
#     client = GGithubClient()
#     assert client.session.closed is False
#     await client.close()
#     assert client.session.closed is True
#     await GGithubClient.reinit()
#     client = GGithubClient()
#     assert client.session.closed is False
#     await GGithubClient.close()
#     assert client.session.closed is True
#     assert GGithubClient().session.closed is False


# @pytest.mark.asyncio
# async def test_post_status(aioresponses, mock_gh_token):
#     _ = mock_gh_token
#     github_repo = "ant31/ffci"
#     ref = "1234"
#     path = f"https://api.github.com/repos/{github_repo}/commits/{ref}/statuses"
#     aioresponses.post(
#         path,
#         status=201,
#         body=GithubCommitStatus(
#             state=GithubCommitStatusStateEnum.PENDING, description="test"
#         ).model_dump_json(),
#     )
#     client = GGithubClient()
#     resp = await client.post_status(
#         github_repo=github_repo,
#         sha=ref,
#         body=CreateGithubCommitStatus(
#             state=GithubCommitStatusStateEnum.PENDING, description="test"
#         ),
#     )
#     assert resp.description == "test"


# # def test_ping_event(ping_data, ping_headers):
# #     ghe = GithubEvent(ping_data, ping_headers)
# #     assert ghe.event_type == "ping"
# #     with pytest.raises(Unsupported):
# #         assert ghe.ref
# #     with pytest.raises(Unsupported):
# #         assert ghe.refname
# #     with pytest.raises(Unsupported):
# #         assert ghe.head_sha
# #     with pytest.raises(Unsupported):
# #         assert ghe.repo == "ant31/jenkinstest"
# #     with pytest.raises(Unsupported):
# #         assert ghe.user


# # def test_push_event(push_data, push_headers):
# #     ghe = GithubEvent(push_data, push_headers)
# #     assert ghe.event_type == "push"
# #     assert ghe.head_sha == "3af890fa500d855c8a2536b9998e43efb25f1460"
# #     assert ghe.istag() is False
# #     assert ghe.ref == "refs/heads/ant31-patch-1"
# #     assert ghe.refname == "ant31-patch-1"
# #     assert ghe.repo == "ant31/jenkinstest"
# #     assert ghe.user == "ant31"


# # def test_pr_event(pr_data, pr_headers):
# #     ghe = GithubEvent(pr_data, pr_headers)
# #     assert ghe.event_type == "pull_request"
# #     assert ghe.head_sha == "495d0b659a0a78855183135c5d427ce79ac43552"
# #     assert ghe.istag() is False
# #     assert ghe.ref == "fix_weave_start"
# #     assert ghe.refname == "fix_weave_start"
# #     assert ghe.repo == "kubernetes-incubator/kargo"
# #     assert ghe.user == "mattymo"
