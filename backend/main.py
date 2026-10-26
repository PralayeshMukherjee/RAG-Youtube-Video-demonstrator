
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv
import os
from youtubeRAG import process_video, ask_question
load_dotenv()

app = FastAPI(title="YouTube RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("frontendurl")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VideoRequest(BaseModel):
    url: HttpUrl


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message": "YouTube RAG API is running"}


@app.post("/api/videos")
def load_video(request: VideoRequest):
    try:
        video_id = process_video(str(request.url))
        return {
            "message": "Video processed successfully",
            "videoId": video_id,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/chat")
def chat(request: ChatRequest):
    try:
        if not request.question.strip():
            raise HTTPException(
                status_code=422, detail="Question cannot be empty"
            )

        answer = ask_question(request.question)

        return {"answer": answer}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate an answer",
        )
