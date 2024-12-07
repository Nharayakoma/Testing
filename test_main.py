import pytest
from fastapi import HTTPException
from httpx import RequestError
import httpx
from main import get_user_gists


@pytest.mark.asyncio
async def test_get_user_gists_success(monkeypatch):
    # Mock successful response data
    mock_gists = [
        {
            "id": "6cad326836d38bd3a7ae",
            "description": "Hello world!",
            "url": "https://gist.github.com/octocat/6cad326836d38bd3a7ae"
        },
        {
            "id": "0831f3fbd83ac4d46451",
            "description": "",
            "url": "https://gist.github.com/octocat/0831f3fbd83ac4d46451"
        },
        {
            "id": "2a6851cde24cdaf4b85b",
            "description": "",
            "url": "https://gist.github.com/octocat/2a6851cde24cdaf4b85b"
        },
        {
            "id": "9257657",
            "description": "Some common .gitignore configurations",
            "url": "https://gist.github.com/octocat/9257657"
        },
        {
            "id": "1305321",
            "description": None,
            "url": "https://gist.github.com/octocat/1305321"
        },
        {
            "id": "1169854",
            "description": None,
            "url": "https://gist.github.com/octocat/1169854"
        },
        {
            "id": "1169852",
            "description": None,
            "url": "https://gist.github.com/octocat/1169852"
        },
        {
            "id": "1162032",
            "description": None,
            "url": "https://gist.github.com/octocat/1162032"
        }
    ]

    class MockResponse:
        status_code = 200

        def json(self):
            return mock_gists

    class MockAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url):
            return MockResponse()

    # Patch httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    # Test the function
    result = await get_user_gists("octocat")

    assert len(result) == 8  # Updated to match the number of mock gists

    # Test the first gist
    assert result[0]["id"] == "6cad326836d38bd3a7ae"
    assert result[0]["description"] == "Hello world!"
    assert result[0]["url"] == "https://gist.github.com/octocat/6cad326836d38bd3a7ae"

    # Test the second gist (empty description)
    assert result[1]["id"] == "0831f3fbd83ac4d46451"
    assert result[1]["description"] == ""  # Empty description
    assert result[1]["url"] == "https://gist.github.com/octocat/0831f3fbd83ac4d46451"

    # Test the third gist (empty description)
    assert result[2]["id"] == "2a6851cde24cdaf4b85b"
    assert result[2]["description"] == ""  # Empty description
    assert result[2]["url"] == "https://gist.github.com/octocat/2a6851cde24cdaf4b85b"

    # Test the fourth gist
    assert result[3]["id"] == "9257657"
    assert result[3]["description"] == "Some common .gitignore configurations"
    assert result[3]["url"] == "https://gist.github.com/octocat/9257657"

    # Test the fifth gist (null description)
    assert result[4]["id"] == "1305321"
    assert result[4]["description"] == "No description"  # Handling None as 'No description'
    assert result[4]["url"] == "https://gist.github.com/octocat/1305321"

    # Test the sixth gist (null description)
    assert result[5]["id"] == "1169854"
    assert result[5]["description"] == "No description"  # Handling None as 'No description'
    assert result[5]["url"] == "https://gist.github.com/octocat/1169854"

    # Test the seventh gist (null description)
    assert result[6]["id"] == "1169852"
    assert result[6]["description"] == "No description"  # Handling None as 'No description'
    assert result[6]["url"] == "https://gist.github.com/octocat/1169852"

    # Test the eighth gist (null description)
    assert result[7]["id"] == "1162032"
    assert result[7]["description"] == "No description"  # Handling None as 'No description'
    assert result[7]["url"] == "https://gist.github.com/octocat/1162032"


@pytest.mark.asyncio
async def test_get_user_gists_user_not_found(monkeypatch):
    class MockResponse:
        status_code = 404

        def json(self):
            return {"message": "Not Found"}

    class MockAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url):
            return MockResponse()

    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    with pytest.raises(HTTPException) as exc_info:
        await get_user_gists("nonexistent-user")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


@pytest.mark.asyncio
async def test_get_user_gists_api_error(monkeypatch):
    class MockAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url):
            raise RequestError("Connection error")

    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    with pytest.raises(HTTPException) as exc_info:
        await get_user_gists("octocat")

    assert exc_info.value.status_code == 500
    assert "Error connecting to GitHub API" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_user_gists_other_error(monkeypatch):
    class MockResponse:
        status_code = 403

        def json(self):
            return {"message": "Rate limit exceeded"}

    class MockAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url):
            return MockResponse()

    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    with pytest.raises(HTTPException) as exc_info:
        await get_user_gists("octocat")

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Rate limit exceeded"
