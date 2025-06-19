from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from autocomplete.dictionary_completion.smart_autocomplete import get_predictions as get_completions
import subprocess
import os
import re
import logging

# === Setup Logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("autocomplete-backend")

# === FastAPI Setup ===
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Request Model ===
class InputRequest(BaseModel):
    input: str

# === Endpoints ===
@app.post("/predict_complete")
def predict_complete(req: InputRequest):
    predictions = get_completions(req.input)
    return {"predictions": predictions}

@app.post("/predict_next")
def predict_next(req: InputRequest):
    model_path = os.getenv("LLM_MODEL", "/Users/christian/Documents/fydp/llama.cpp/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
    predictions = run_llm_prediction(req.input, model_path)
    return {"predictions": predictions}

# === LLM Runner ===
def run_llm_prediction(prompt, model_path):
    formatted_prompt = f"Complete this sentence with likely next words:\n{prompt.strip()}"

    cmd = [
        "/Users/christian/Documents/fydp/llama.cpp/build/bin/llama-cli",
        "-m", model_path,
        "--prompt", formatted_prompt,
        "--n-predict", "20",
        "--temp", "0.7",
        "--top-k", "40",
        "--top-p", "0.95",
        "--repeat-penalty", "1.1",
        "--no-conversation"
    ]

    try:
        logger.info(f"Running LLM with prompt: {formatted_prompt}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        logger.info(f"STDOUT:\n{result.stdout}")
        logger.info(f"STDERR:\n{result.stderr}")

        output = result.stdout.strip()

        if formatted_prompt in output:
            suffix = output.split(formatted_prompt, 1)[-1].strip()
        else:
            suffix = output.strip()

        words = re.findall(r'\b[a-zA-Z]+\b', suffix)
        cleaned_words = []

        for word in words:
            clean = word.lower()
            if clean and len(clean) > 1:
                cleaned_words.append(clean)

        unique_words = []
        seen = set()
        for word in cleaned_words:
            if word not in seen:
                unique_words.append(word)
                seen.add(word)

        return unique_words[:3] if unique_words else ["the", "and", "of"]

    except subprocess.TimeoutExpired:
        logger.error("LLM subprocess timed out.")
        return ["the", "and", "of"]
    except Exception as e:
        logger.error(f"LLM subprocess failed: {e}")
        return ["the", "and", "of"]
