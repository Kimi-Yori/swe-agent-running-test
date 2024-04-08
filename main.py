from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
from cohere import Client

app = FastAPI()

client = Client(api_key=os.getenv("COHERE_API_KEY"))

@app.post("/command-r-plus")
async def command_r_plus(request: Request):
    data = await request.json()
    text = data.get("text")

    if not text:
        return JSONResponse(status_code=400, content={"error": "テキスト パラメーターが指定されていません"})

    # Cohere Command R Plus を呼び出す
    response = client.command_r_plus(text)

    return JSONResponse(content=response.results)