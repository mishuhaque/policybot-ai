"""FastAPI application exposing the PolicyBot retrieval pipeline with JWT authentication."""

from __future__ import annotations

from datetime import timedelta
from typing import Optional

from fastapi import Body, Depends, FastAPI, Form, HTTPException
from pydantic import BaseModel, Field

from .rag_pipeline import PolicyAnswer, query_policies
from .auth import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI(title="PolicyBot", description="Ask questions about policy documents with JWT authentication.")


class QueryRequest(BaseModel):
    """Expected payload for POST /ask requests."""

    query: str = Field(..., min_length=1, description="User question about policies")
    top_k: int = Field(3, ge=1, le=10, description="Number of policy chunks to retrieve")


class TokenResponse(BaseModel):
    """Response from token endpoint."""

    access_token: str
    token_type: str
    expires_in: int


@app.get("/", summary="Health check")
def home() -> dict[str, str]:
    """Simple endpoint to verify the service is running."""

    return {"msg": "PolicyBot API is running"}


@app.post("/token", response_model=TokenResponse, summary="Get JWT authentication token")
async def login_for_access_token(username: str = Form(...)) -> TokenResponse:
    """Generate a JWT bearer token for API access."""

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@app.post("/ask", response_model=PolicyAnswer, summary="Retrieve and summarize policies")
async def ask_policy(
    payload: Optional[QueryRequest] = Body(default=None),
    query: Optional[str] = Form(default=None),
    top_k: int = Form(default=3),
    username: str = Depends(verify_token) = None,
) -> PolicyAnswer:
    """Answer a policy-related question using the RAG pipeline.

    The endpoint accepts either a JSON body matching :class:`QueryRequest` or
    traditional form-encoded parameters for backwards compatibility.
    Requires a valid JWT token via Authorization header.
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
        result["requested_by"] = username
    except FileNotFoundError as exc:  # pragma: no cover - depends on runtime state
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return result


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
