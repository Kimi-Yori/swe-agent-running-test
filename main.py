from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse  # StreamingResponseをインポート
from pydantic import BaseModel, ValidationError
import os
import cohere
from cohere import CohereError

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    stream: bool = False

api_key = os.getenv("COHERE_API_KEY")
if not api_key:
    raise EnvironmentError("COHERE_API_KEY is not set in environment variables. Please set it to continue.")
co = cohere.Client(api_key=api_key)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

@app.exception_handler(CohereError)
async def cohere_exception_handler(request, exc: CohereError):
    return JSONResponse(status_code=500, content={"error": "Cohere API error"})

@app.post("/chat")
async def chat(request_data: ChatRequest):
    try:
        data = request_data.dict()
        data["model"] = "command-r-plus"  # Specify the model
        if data["stream"]:
            stream = co.chat_stream(**data)
            return StreamingResponse(stream)
        else:
            response = co.chat(**data)
            return JSONResponse(content=response)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
