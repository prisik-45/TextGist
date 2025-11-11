# Text Summarizer

A simple text summarization web application with a Streamlit frontend and FastAPI backend.

## Features

- 📝 Simple and minimal UI design
- 🚀 FastAPI backend for API handling
- 🎨 Streamlit frontend for user interaction
- 🤖 AI-powered text summarization using OpenAI API

## Prerequisites

- Python 3.8+
- CHATBOT_API_KEY environment variable set with your OpenAI API key

## Installation

Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Application

### 1. Start the FastAPI Backend

Open a terminal and run:

```bash
uvicorn backend:app --reload --port 8000
```

The backend will start on `http://localhost:8000`

### 2. Start the Streamlit Frontend

Open another terminal and run:

```bash
streamlit run frontend.py
```

The frontend will open in your browser at `http://localhost:8501`

## Usage

1. Enter or paste your text in the text area
2. Click the "Summarize" button
3. View the generated summary

## API Endpoints

- `GET /` - API information
- `POST /summarize` - Summarize text
- `GET /health` - Health check

## Environment Variables

- `CHATBOT_API_KEY` - Your OpenAI API key (must be set in system environment variables)
