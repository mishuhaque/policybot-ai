from fastapi import FastAPI, Form
from rag_pipeline import query_policies

app = FastAPI()

@app.get("/")
def home():
    return {"msg": "PolicyBot API is running"}

@app.post("/ask")
async def ask_policy(query: str = Form(...)):
    result = query_policies(query)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
