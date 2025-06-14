# backend.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from autocomplete.dictionary_completion.smart_autocomplete import get_predictions as get_completions
import subprocess
import os

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
    formatted_prompt = f"Complete this sentence with one likely next word:\n{prompt.strip()}"
    cmd = [
        "../../llama.cpp/build/bin/llama-cli",
        "-m", model_path,
        "--prompt", formatted_prompt,
        "--n-predict", "3",
        "--temp", "0.5",
        "--top-k", "40",
        "--top-p", "0.95",
        "--repeat-penalty", "1.1",
        "-no-cnv"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout.strip()

        if formatted_prompt in output:
            suffix = output.split(formatted_prompt, 1)[-1].strip()
        else:
            suffix = output.strip()

        tokens = suffix.split()
        cleaned = [''.join(c for c in tok if c.isalpha()).lower() for tok in tokens]
        for word in cleaned:
            if word:
                return [word]
        return ["[No valid prediction]"]
    except Exception as e:
        return [f"[LLM Error: {e}]"]
