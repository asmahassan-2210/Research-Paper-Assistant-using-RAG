import os
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from rag_engine import RAGAssistant

load_dotenv()

app = FastAPI(
    title="Research Paper Assistant RAG API",
    description="Backend service to index research PDFs and execute strictly context-bounded Q&A.",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize RAG Engine with Google Gemini API Key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY environment variable is not set.")

rag_assistant = RAGAssistant(google_api_key=api_key)


class QueryRequest(BaseModel):
    question: str


# Serve index.html from templates folder
@app.get("/", response_class=HTMLResponse)
async def read_root():
    template_path = os.path.join("templates", "index.html")
    if not os.path.exists(template_path):
        raise HTTPException(
            status_code=404, 
            detail="templates/index.html not found. Please create the file."
        )
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


@app.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload one or multiple PDF research papers.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    file_tuples = []
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400, 
                detail=f"File '{file.filename}' is not a PDF. Only PDF formats are supported."
            )
        content = await file.read()
        file_tuples.append((file.filename, content))

    try:
        result = rag_assistant.process_pdfs(file_tuples)
        return {
            "message": "Documents indexed successfully.",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
def query_documents(request: QueryRequest):
    """
    Query the indexed research papers.
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        response = rag_assistant.answer_question(request.question)
        return response
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)