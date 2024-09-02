import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langserve import add_routes
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
import uvicorn
from docx import Document
from PyPDF2 import PdfReader

# Load environment variables
load_dotenv()

# Set environment variables for tracing
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGSMITH_API_KEY")
os.environ['LANGCHAIN_TRACING_V2'] = "true"

# FastAPI app configuration
app = FastAPI(
    title="Langchain Server",
    version="1.0",
    description="A simple API Server for Question Answering"
)

# Functions to read files
def read_pdf_file(file_path):
    pdf_text = ""
    reader = PdfReader(file_path)
    for page in reader.pages:
        pdf_text += page.extract_text()
    return pdf_text

def read_word_file(file_path):
    doc = Document(file_path)
    word_text = ""
    for paragraph in doc.paragraphs:
        word_text += paragraph.text + "\n"
    return word_text

def load_files():
    pdf1 = read_pdf_file('India A Comprehensive Overview.pdf')
    pdf2 = read_pdf_file('Indias Diverse States and Territories.pdf')
    word1 = read_word_file('Indias_Education_Healthcare_and_Social_Development.docx')
    word2 = read_word_file('documentsIndias_Natural_Beauty_and_Wildlife.docx')
    return word1 + "\n" + word2 + "\n" + pdf1 + "\n" + pdf2

# Load all text
all_text = load_files()

# LangChain prompt and model configuration
prompt_template = ChatPromptTemplate.from_template(
    template="Based on the following context, please provide a concise and accurate answer to the question.\n\nContext: {context}\n\nQuestion: {question}\nAnswer:"
)
model = ChatOpenAI(temperature=0.7)
qa_chain = prompt_template | model

# Add LangChain routes to FastAPI app
add_routes(app, qa_chain, path="/answer")

@app.post("/answer")
def answer_question(question: dict):
    question_text = question.get("question", "")
    if not question_text:
        raise HTTPException(status_code=400, detail="Question not provided")
    response = qa_chain.invoke({"question": question_text, "context": all_text})
    return {"answer": response}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)


