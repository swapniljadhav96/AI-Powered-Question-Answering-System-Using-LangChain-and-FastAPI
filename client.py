import os
import streamlit as st
import requests

# Load environment variables from Streamlit Secrets
langsmith_api_key = st.secrets["LANGSMITH_API_KEY"]
openai_api_key = st.secrets["OPENAI_API_KEY"]

# Ensure LANGSMITH_API_KEY is set
if not langsmith_api_key:
    raise ValueError("LANGSMITH_API_KEY is not set. Please check your Streamlit secrets.")

# Set environment variables for tracing
os.environ['LANGCHAIN_API_KEY'] = langsmith_api_key
os.environ['LANGCHAIN_TRACING_V2'] = "true"

# FastAPI endpoint URL
API_URL = "http://localhost:8000/answer"

def get_answer_response(question):
    # Send the question to the FastAPI server
    response = requests.post(API_URL, json={"question": question})
    
    if response.status_code == 200:
        json_response = response.json()
        # Extract the content from the JSON response
        answer_content = json_response.get('answer', {}).get('content', 'No answer found')
        return answer_content
    else:
        return f"Error: {response.status_code} - {response.text}"

# Streamlit UI
st.title('Question Answering System')

# User input for the question
question = st.text_input("Enter your question:")

# Display the answer on submit
if question:
    answer = get_answer_response(question)
    st.write(answer)
