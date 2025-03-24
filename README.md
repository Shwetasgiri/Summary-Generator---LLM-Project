# SAMMARYIT

An AI-powered document analysis tool that generates intelligent summaries from multiple documents and provides similarity analysis.

## About

SAMMARYIT is an advanced multi-document analysis system that processes documents (PDF, DOCX, TXT) and compares their content using the BART language model. It features real-time similarity analysis and a clean web interface, built with FastAPI for efficiency and scalability.

## Features

- Multi-document summarization using BART-based abstractive techniques
- Document similarity analysis using TF-IDF and cosine similarity
- Support for PDF, DOCX, and TXT file formats
- Interactive web interface with real-time processing
- Similarity matrix visualization for document comparisons

## Setup

1. Clone the repository
```bash
git clone [your-repo-url]
cd SAMMARYIT
```

## Installation

1. Create virtual environment
```bash
python -m venv venv
```

2. Activate virtual environment

Windows:
```cmd
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run application
```bash
python app.py
```

5. Open http://localhost:8000 in your browser

## Usage

1. Upload multiple documents or paste text directly
2. View generated summaries for each document
3. Analyze similarity scores between documents in the matrix
4. Access results through the intuitive web interface

## Tech Stack

- Backend: FastAPI, Transformers (facebook/bart-large-cnn)
- Document Processing: PyPDF2, python-docx
- Text Analysis: scikit-learn (TF-IDF, Cosine Similarity)
- Frontend: HTML, CSS, JavaScript

## Project Status

MSc Dissertation Project, University of Liverpool (2024)

## Author

Shweta Giri - MSc Computer Science, University of Liverpool
