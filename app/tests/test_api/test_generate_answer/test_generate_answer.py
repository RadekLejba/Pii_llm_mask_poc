import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from main import app
from mock import AsyncMock, MagicMock, patch


client = TestClient(app)


class TestGenerateAnswerEndpoint:
    @patch("api.generate_answer.generate_answer.client", new_callable=AsyncMock)
    @pytest.mark.anyio
    async def test_generate_answer(self, mock_huggingface_client):
        async_iterable_mock = AsyncMock()
        async_iterable_mock.__aiter__.return_value = [
            MagicMock(choices=[MagicMock(delta=MagicMock(content="Test"))]),
            MagicMock(choices=[MagicMock(delta=MagicMock(content=" Response"))]),
        ]
        mock_huggingface_client.chat.completions.create.return_value = (
            async_iterable_mock
        )
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.post(
                "/generate_answer/", json={"prompt": "Test", "context": "test"}
            )

        assert response.status_code == 200
        assert response.json() == {"response": "Test Response"}
