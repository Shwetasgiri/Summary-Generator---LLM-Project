import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
import docx
from transformers import pipeline
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging
import uvicorn
import tempfile
import numpy as np

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the current directory as the static directory
app.mount("/static", StaticFiles(directory="."), name="static")

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        if not text.strip():
            logging.warning(f"Extracted empty text from PDF: {file_path}")
            return "No readable text found in the PDF."
        
        logging.info(f"Successfully extracted {len(text)} characters from PDF: {file_path}")
        return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF {file_path}: {str(e)}")
        raise

def extract_text_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        logging.error(f"Error extracting text from DOCX: {str(e)}")
        raise

def generate_summary(text, max_length=150):
    try:
        input_text = " ".join(text.split()[:1024])
        logging.info(f"Attempting to summarize text of length: {len(input_text)}")
        
        if not input_text.strip():
            logging.warning("Empty input text provided for summarization")
            return "Unable to generate summary: Empty input text"
        
        summary = summarizer(input_text, max_length=max_length, min_length=min(40, max_length-10), do_sample=False)
        
        if summary and len(summary) > 0:
            logging.info(f"Successfully generated summary of length: {len(summary[0]['summary_text'])}")
            return summary[0]['summary_text']
        else:
            logging.error("Summary generation failed: Empty result from summarizer")
            return "Summary generation failed: Empty result from summarizer"
    except Exception as e:
        logging.error(f"Unexpected error in summary generation: {str(e)}")
        return f"Summary generation failed: {str(e)}"

def calculate_similarity_matrix(documents):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    cosine_sim = cosine_similarity(tfidf_matrix)
    return cosine_sim

@app.get("/")
async def read_root():
    return FileResponse("index.html")

@app.get("/script.js")
async def serve_script():
    return FileResponse("script.js")

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('favicon.ico')

@app.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    summary_length: int = Form(150)
):
    logging.info(f"Received upload request. Files: {[f.filename for f in files]}")
    logging.info(f"Summary length: {summary_length}")
    
    documents = []
    temp_files = []
    try:
        for file in files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                temp_files.append(temp_file.name)
                contents = await file.read()
                temp_file.write(contents)
            
            file_extension = os.path.splitext(file.filename)[1].lower()
            
            if file_extension == ".pdf":
                text = extract_text_from_pdf(temp_file.name)
            elif file_extension == ".docx":
                text = extract_text_from_docx(temp_file.name)
            elif file_extension == ".txt":
                with open(temp_file.name, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            documents.append(text)
            logging.info(f"Successfully processed file: {file.filename} (length: {len(text)} characters)")

        summaries = []
        for i, doc in enumerate(documents):
            logging.info(f"Generating summary for document {i+1} (length: {len(doc)} characters)")
            summary = generate_summary(doc, max_length=summary_length)
            summaries.append(summary)
            logging.info(f"Generated summary for document {i+1}: {summary[:100]}...")
        
        similarity_matrix = calculate_similarity_matrix(documents)
        
        logging.info(f"Processing complete. Returning response with {len(summaries)} summaries")
        return {
            "summaries": summaries,
            "original_texts": documents,
            "similarity_matrix": similarity_matrix.tolist()
        }
    except Exception as e:
        logging.error(f"An error occurred during processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred during processing: {str(e)}")
    finally:
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except Exception as e:
                logging.error(f"Error deleting temporary file {temp_file}: {str(e)}")

@app.post("/summarize-text")
async def summarize_text(
    text: str = Form(...),
    summary_length: int = Form(150)
):
    logging.info(f"Received text summarization request. Text length: {len(text)}")
    logging.info(f"Summary length: {summary_length}")
    
    try:
        summary = generate_summary(text, max_length=summary_length)
        logging.info(f"Generated summary (length: {len(summary)} characters)")
        return {
            "summaries": [summary],
            "original_texts": [text],
            "similarity_matrix": None
        }
    except Exception as e:
        logging.error(f"An error occurred during text summarization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred during text summarization: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)