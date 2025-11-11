import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import httpx
from docx import Document
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
import requests
from text_processor import preprocess_text

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8501",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("CHATBOT_API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable not set.")

def read_docx(file):
    document = Document(file)
    return "\n".join([paragraph.text for paragraph in document.paragraphs])

def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

async def fetch_url_content(url: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.extract()
            paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])
            text = ' '.join([p.get_text() for p in paragraphs])
            return text
    except httpx.RequestError as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing URL content: {e}")

@app.post("/summarize")
async def summarize_text(
    text_input: str = Form(None),
    file: UploadFile = File(None),
    url: str = Form(None),
    summary_length: str = Form("medium")
):
    input_text_content = ""
    if text_input:
        input_text_content = text_input
    elif file:
        file_extension = file.filename.split('.')[-1].lower()
        try:
            if file_extension == "pdf":
                input_text_content = read_pdf(file.file)
            elif file_extension == "docx":
                input_text_content = read_docx(file.file)
            else:
                raise HTTPException(status_code=400, detail="Unsupported file type. Only PDF and DOCX are allowed.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading file: {e}")
    elif url:
        input_text_content = await fetch_url_content(url)
    else:
        raise HTTPException(status_code=400, detail="No input provided. Please provide text, upload a file, or enter a URL.")
    if not input_text_content.strip():
        raise HTTPException(status_code=400, detail="Input text is empty. Please provide content to summarize.")

    # text preprocessing 
    processed_text = preprocess_text(input_text_content)
    processed_text = processed_text[:12000]

    length_prompt = {
        "short": "Provide a very concise summary, ideally 2-3 sentences.",
        "medium": "Provide a moderately detailed summary, covering main points.",
        "long": "Provide a detailed summary, including key supporting details and examples.",
    }.get(summary_length, "Provide a concise summary.")

    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://textgist.vercel.app",
            "X-Title": "TextGist Summarizer",
        }
        payload = {
            "model": "meta-llama/llama-3.3-8b-instruct:free",
            "messages": [
                {"role": "system", "content": f"You are a helpful text summarization assistant. {length_prompt}"},
                {"role": "user", "content": f"Summarize the following text:\n\n{processed_text}"}
            ],
            "stream": False,
        }
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        summary = data["choices"][0]["message"]["content"]
        return {"summary": summary}
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {resp.status_code} - {resp.text}")
        raise HTTPException(status_code=resp.status_code, detail=f"API returned {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"Error summarizing text: {e}")
        raise HTTPException(status_code=500, detail=f"Error summarizing text: {e}")
