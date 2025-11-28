# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.views.pdf_rag import router as pdf_rag_router
import uvicorn

app = FastAPI(
    title="Gemini 2.5 Flash PDF RAG API",
    description="3-step flow: upload → query → cleanup | Raw Gemini responses",
    version="3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pdf_rag_router)

@app.get("/")
def home():
    return {"message": "Gemini PDF RAG API Ready → /docs"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)