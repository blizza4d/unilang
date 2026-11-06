import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_stream_emits_stage_and_result_events():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/extract/stream",
            files={"file": ("invoice.pdf", b"%PDF-mock-bytes-test-stream", "application/pdf")},
        )
        assert response.status_code == 200
        text = response.text
        # Assert stage events are emitted
        assert "event: stage" in text
        # Assert result event is emitted (Catches Mutation 2: renaming SSE result event)
        assert "event: result" in text
