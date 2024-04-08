from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import os
from cohere import Client, CohereError

app = FastAPI()
client = Client(api_key=os.getenv("COHERE_API_KEY"))

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

@app.exception_handler(CohereError)
async def cohere_exception_handler(request: Request, exc: CohereError):
    return JSONResponse(status_code=500, content={"error": "Cohere APIエラー"})

async def validate_request(request: Request):
    data = await request.json()
    text = data.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="テキストパラメーターが指定されていません")
    return text

async def process_request(text: str):
    try:
        response = client.command_r_plus(text)
        return response.results
    except CohereError as e:
        raise e

@app.post("/command-r-plus")
async def command_r_plus(request: Request):
    text = await validate_request(request)
    result = await process_request(text)
    return JSONResponse(content=result)