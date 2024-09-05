from fastapi import FastAPI, HTTPException, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from bs4 import BeautifulSoup
import requests
import uuid
import logging
import PyPDF2
from chat import find_most_similar_content

app = FastAPI()

# In-memory storage for simplicity
stored_content = {}

# Set up logging
logging.basicConfig(filename='content_log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

templates = Jinja2Templates(directory='templates')

# HTML Homepage
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

# Model for API request
class URLRequest(BaseModel):
    url: str

# Process URL API (via POST request)
@app.post("/process_url")
async def process_url(url: str = Form()):
    # Fetch the URL content
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Parse and clean the content
    soup = BeautifulSoup(response.text, 'html.parser')
    if "You can’t perform that action at this time" in response.text:
        print("Access blocked for this page.")
        # Log the content with the URL ID
        logging.info(f"URL ID: 'null, URL: {url}, Content: Access blocked for this page.")
        return {
            "chat_id": 'null',
            "message": "Access blocked for this page."
        }  
    
    else:
        cleaned_content = soup.get_text(separator= ' ', strip= True)

        # Replace multiple spaces with a single space
        cleaned_content = ' '.join(cleaned_content.split())
    

        # Generate a unique chat_id
        chat_id = str(uuid.uuid4())

        # Store the cleaned content with the unique chat_id
        stored_content[chat_id] = cleaned_content

        # Log the content with the URL ID
        logging.info("CHAT ID: %s, URL: %s, Content: %s...", chat_id, url, cleaned_content)

        return {
            "chat_id": chat_id,
            "message": "URL content processed and stored successfully."
        }   

# For API-based usage (without HTML form)
@app.post("/api/process_url")
async def process_url_api(request: URLRequest):
    return await process_url(url=request.url)

# Process PDF Document API (via POST request)
@app.post("/process_pdf")
async def process_pdf(pdf_file: UploadFile = File(...)):
    try:
        # Read the PDF file
        pdf_reader = PyPDF2.PdfReader(pdf_file.file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # Clean the extracted text
        cleaned_text = ' '.join(text.split())

        # Generate a unique chat_id
        chat_id = str(uuid.uuid4())

        # Store the cleaned text with the unique chat_id
        stored_content[chat_id] = cleaned_text

        # Log the content with the chat_id
        logging.info(f"CHAT ID: {chat_id}, File Name: {pdf_file.filename}, Content: {cleaned_text}...")

        return {
            "chat_id": chat_id,
            "message": "PDF content processed and stored successfully."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to process PDF document.")
    
@app.post("/chat")
async def chat(chat_id: str = Form(...), question: str = Form(...)):

    # Use chat.py function to find the most relevant content
    key,content,score = find_most_similar_content(chat_id, question)
    response = score, content

    return {
        "response": response
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)