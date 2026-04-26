from datetime import timedelta
from fastapi import FastAPI, Form, Depends
from .rag_pipeline import query_policies
from .auth import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI(title="PolicyBot API", version="1.0.0")

@app.get("/")
def home():
    return {"msg": "PolicyBot API is running"}

@app.post("/token")
async def login_for_access_token(username: str = Form(...)):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.post("/ask")
async def ask_policy(query: str = Form(...), username: str = Depends(verify_token)):
    result = query_policies(query)
    result["requested_by"] = username
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
