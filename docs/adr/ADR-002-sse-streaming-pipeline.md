# ADR-002: Server-Sent Events (SSE) Streaming Pipeline

## Status
Accepted

## Context
Document understanding tasks involving multimodal vision and verification take between 3 to 10 seconds. Traditional synchronous REST endpoints block the client without intermediate feedback, creating a perception of unresponsiveness and causing network timeouts on slow connections.

## Decision
We implemented a chunked HTTP Server-Sent Events (SSE) streaming pipeline via `POST /api/v1/extract/stream`. As each agent in the LangGraph pipeline finishes execution, it pushes an event (`agent_start`, `agent_complete`, `grounding_ready`, `final_result`) to an `asyncio.Queue` that streams formatted `text/event-stream` chunks to the browser.

## Consequences
- Immediate visual feedback in the UI with sub-500ms first milestone response.
- Real-time latency tracking and token consumption metrics per agent stage.
- Graceful error containment: if an agent fails, an explicit `error` event halts the stream without crashing the connection.
