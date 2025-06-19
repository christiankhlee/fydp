# backend.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from autocomplete.dictionary_completion.smart_autocomplete import get_predictions as get_completions
import subprocess
import os
import re

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputRequest(BaseModel):
    input: str

@app.post("/predict_complete")
def predict_complete(req: InputRequest):
    predictions = get_completions(req.input)
    return {"predictions": predictions}

@app.post("/predict_next")
def predict_next(req: InputRequest):
    model_path = os.getenv("LLM_MODEL", "../../llama.cpp/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
    predictions = run_llm_prediction(req.input, model_path)
    return {"predictions": predictions}

def run_llm_prediction(prompt, model_path):
    formatted_prompt = f"Complete this sentence with likely next words:\n{prompt.strip()}"
    cmd = [
        "../../llama.cpp/build/bin/llama-cli",
        "-m", model_path,
        "--prompt", formatted_prompt,
        "--n-predict", "20",  # Increased to get more tokens
        "--temp", "0.7",      # Slightly higher temperature for variety
        "--top-k", "40",
        "--top-p", "0.95",
        "--repeat-penalty", "1.1",
        "-no-cnv"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout.strip()

        if formatted_prompt in output:
            suffix = output.split(formatted_prompt, 1)[-1].strip()
        else:
            suffix = output.strip()

        # Extract words from the output
        words = re.findall(r'\b[a-zA-Z]+\b', suffix)
        
        # Clean and filter words
        cleaned_words = []
        for word in words:
            clean_word = word.lower()
            if clean_word and len(clean_word) > 1:  # Filter out single letters
                cleaned_words.append(clean_word)
        
        # Remove duplicates while preserving order
        unique_words = []
        seen = set()
        for word in cleaned_words:
            if word not in seen:
                unique_words.append(word)
                seen.add(word)
        
        # Return up to 3 predictions
        if len(unique_words) >= 3:
            return unique_words[:3]
        elif len(unique_words) > 0:
            # Pad with empty strings if we have fewer than 3
            return unique_words + [""] * (3 - len(unique_words))
        else:
            return ["the", "and", "of"]  # Fallback common words
            
    except subprocess.TimeoutExpired:
        return ["the", "and", "of"]  # Fallback on timeout
    except Exception as e:
        print(f"LLM Error: {e}")
        return ["the", "and", "of"]  # Fallback on error