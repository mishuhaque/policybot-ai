"""FastAPI application exposing the PolicyBot retrieval pipeline."""

from __future__ import annotations

from typing import Optional

from fastapi import Body, FastAPI, Form, HTTPException
from pydantic import BaseModel, Field

from rag_pipeline import PolicyAnswer, query_policies

app = FastAPI(title="PolicyBot", description="Ask questions about policy documents.")


class QueryRequest(BaseModel):
    """Expected payload for POST /ask requests."""

    query: str = Field(..., min_length=1, description="User question about policies")
    top_k: int = Field(3, ge=1, le=10, description="Number of policy chunks to retrieve")


@app.get("/", summary="Health check")
def home() -> dict[str, str]:
    """Simple endpoint to verify the service is running."""

    return {"msg": "PolicyBot API is running"}


@app.post("/ask", response_model=PolicyAnswer, summary="Retrieve and summarize policies")
async def ask_policy(
    payload: Optional[QueryRequest] = Body(default=None),
    query: Optional[str] = Form(default=None),
    top_k: int = Form(default=3),
) -> PolicyAnswer:
    """Answer a policy-related question using the RAG pipeline.

    The endpoint accepts either a JSON body matching :class:`QueryRequest` or
    traditional form-encoded parameters for backwards compatibility.
    """

    if payload is not None:
        query_text = payload.query
        top_k_value = payload.top_k
    elif query is not None:
        query_text = query
        top_k_value = top_k
    else:
        raise HTTPException(status_code=422, detail="A 'query' parameter is required.")

    try:
        result = query_policies(query_text, top_k=top_k_value)
    except FileNotFoundError as exc:  # pragma: no cover - depends on runtime state
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return result


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
