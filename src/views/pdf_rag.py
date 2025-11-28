# src/views/pdf_rag.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from src.file_manager import upload_pdfs, query_gemini, cleanup
import shutil
import tempfile
import os
from typing import List

router = APIRouter(prefix="/pdf-rag", tags=["PDF Chatbot"])

@router.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    temp_paths = []
    try:
        for f in files:
            if not f.filename.lower().endswith(".pdf"):
                raise HTTPException(400, "Only PDF files allowed")
            temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            shutil.copyfileobj(f.file, temp)
            temp_paths.append(temp.name)
            temp.close()

        uploaded = upload_pdfs(temp_paths)
        return {
            "message": "Files ready! You can now ask questions.",
            "uploaded_files": uploaded
        }
    finally:
        for p in temp_paths:
            try: os.unlink(p)
            except: pass

@router.post("/query")
async def query(question: str = Form(...)):
    try:
        result = query_gemini(question)
        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "tip": "Ask me anything about your PDFs!"
        }
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.post("/cleanup")
async def clean():
    result = cleanup()
    return {
        "message": "All files cleared. Upload new ones to continue!",
        **result
    }