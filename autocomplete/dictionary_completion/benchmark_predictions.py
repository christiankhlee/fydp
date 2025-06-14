import subprocess
import time
import json

LLAMA_BIN = "../../llama.cpp/build/bin/llama-cli"  # Update this if needed
MODEL_PATH = "../../llama.cpp/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"  # Or your current model

TEST_PROMPTS = [
    "I want to play",
    "She went to the store to buy",
    "It was a beautiful day to go for a",
    "He studied all night because he had a",
    "They built the house using wood and"
]

N_PREDICT_VALUES = [1, 2, 3, 5]

def run_prediction(prompt, n_predict):
    full_prompt = f"Complete this sentence with one likely next word:\n{prompt}"
    cmd = [
        LLAMA_BIN,
        "-m", MODEL_PATH,
        "--prompt", full_prompt,
        "--n-predict", str(n_predict),
        "--temp", "0.3",
        "--top-k", "40",
        "--top-p", "0.9",
        "--repeat-penalty", "1.1",
        "-no-cnv"
    ]

    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - start

    output = result.stdout.strip()
    suffix = output.split(prompt, 1)[-1].strip() if prompt in output else output.strip()
    token = suffix.split()[0] if suffix else "[None]"

    return token, round(duration, 2)

def main():
    for prompt in TEST_PROMPTS:
        print(f"\nPrompt: \"{prompt}\"")
        for n in N_PREDICT_VALUES:
            token, duration = run_prediction(prompt, n)
            print(f"  n={n:<2} → Prediction: {token:<15} Time: {duration}s")

if __name__ == "__main__":
    main()
