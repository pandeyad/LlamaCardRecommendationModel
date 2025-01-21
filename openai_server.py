from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Set your OpenAI API key (replace with your actual API key)
openai.api_key = os.environ['OPENAI_API_KEY']

# Define the request schema
class InferenceRequest(BaseModel):
    prompt: str
    max_tokens: int = 1000
    temperature: float = 0.7

# Route to serve inference requests
@app.post("/predict")
async def predict(request: InferenceRequest):
    prompt = request.prompt
    max_tokens = request.max_tokens
    temperature = request.temperature

    try:
        # Call OpenAI API to generate a response based on the prompt
        response = openai.Completion.create(
            engine="text-davinci-003",  # Choose the OpenAI model you want to use (e.g., davinci, curie, etc.)
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # Extract and return the generated response
        result = response.choices[0].text.strip()
        return {"response": result}

    except Exception as e:
        return {"error": str(e)}

# Run the server with Uvicorn (run this script or use the command below)
