from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import os
import cohere
from cohere import CohereError

app = FastAPI()
co = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

@app.exception_handler(CohereError)
async def cohere_exception_handler(request: Request, exc: CohereError):
    return JSONResponse(status_code=500, content={"error": "Cohere APIエラー"})

async def validate_request(request: Request):
    data = await request.json()
    message = data.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="messageパラメーターが指定されていません")
    return data

async def process_request(data: dict):
    try:
        data["model"] = "command-r-plus"  # Add this line to use command-r-plus model
        if data.get("stream", False):
            stream = co.chat_stream(**data)
            return StreamingResponse(stream)
        else:
            response = co.chat(**data)
            return JSONResponse(content=response)
    except CohereError as e:
        raise e

@app.post("/chat")
async def chat(request: Request):
    data = await validate_request(request)
    result = await process_request(data)
    return result