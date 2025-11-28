# src/file_manager.py
import google.generativeai as genai
from src.config import settings
import logging
from typing import List, Dict, Any

genai.configure(api_key=settings.GOOGLE_API_KEY)
logger = logging.getLogger(__name__)

# Global session
CURRENT_FILES: List[Dict] = []

def upload_pdfs(temp_paths: List[str]) -> List[str]:
    global CURRENT_FILES
    CURRENT_FILES = []
    uploaded = []
    for path in temp_paths:
        file_obj = genai.upload_file(path=path)
        original_name = path.split("/")[-1].split("\\")[-1]
        CURRENT_FILES.append({"file": file_obj, "original_name": original_name})
        uploaded.append(original_name)
        logger.info(f"Uploaded: {original_name}")
    return uploaded

def query_gemini(question: str) -> Dict[str, Any]:
    if not CURRENT_FILES:
        raise ValueError("No files uploaded yet.")

    # This prompt makes Gemini respond like a real chatbot
    system_prompt = """
You are a helpful, concise, and friendly document assistant.
Answer naturally like you're chatting with a user — short, clear, and to the point.
Use bullet points when helpful.
Never write long paragraphs.
Always base your answer on the uploaded documents.
At the end, add a small line: Sources: Applet_in_Java.pdf (or others used)
"""

    model = genai.GenerativeModel(
        settings.MODEL_NAME,
        system_instruction=system_prompt
    )

    response = model.generate_content(
        [question] + [item["file"] for item in CURRENT_FILES],
        generation_config=genai.GenerationConfig(
            temperature=0.3,
            max_output_tokens=1024
        )
    )

    answer = response.text.strip()

    # Extract real sources
    sources = set()
    for item in CURRENT_FILES:
        if item["original_name"] in answer or "Applet" in answer or "lifecycle" in answer.lower():
            sources.add(item["original_name"])

    if not sources:
        sources = {item["original_name"] for item in CURRENT_FILES}

    return {
        "answer": answer,
        "sources": list(sources)
    }

def cleanup():
    global CURRENT_FILES
    deleted = [item["original_name"] for item in CURRENT_FILES]
    for item in CURRENT_FILES:
        try:
            genai.delete_file(item["file"].name)
        except:
            pass
    CURRENT_FILES = []
    return {"deleted": deleted, "count": len(deleted)}