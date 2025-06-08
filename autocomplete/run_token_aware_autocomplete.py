import subprocess
import sys
import json
import os

# Default model path (you can override with --model flag)
DEFAULT_MODEL = "../llama.cpp/models/Phi-2.Q4_K_M.gguf"
LLAMA_BIN = "../llama.cpp/build/bin/llama-cli"
TOKENIZER_BIN = "../llama.cpp/build/bin/llama-tokenize"

def tokenize(text, model_path):
    cmd = [
        TOKENIZER_BIN,
        "-m", model_path,
        "--prompt", text
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        print("\n--- Raw Tokenizer Output ---")
        print(proc.stdout)
        print("--- End of Tokenizer Output ---\n")

        tokens = proc.stdout.strip().splitlines()
        return tokens
    except Exception as e:
        print(f"Tokenizer error: {e}")
        return []



def generate_completion(prompt, model_path):
    cmd = [
        LLAMA_BIN,
        "-m", model_path,
        "--prompt", prompt,
        "--n-predict", "1",
        "--temp", "0.2",
        "--top-k", "10",
        "--top-p", "0.95",
        "--repeat-penalty", "1.1",
        "-no-cnv"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"[Generation error: {e}]"

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="Text before the cursor")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Path to model file")
    args = parser.parse_args()

    text = args.text
    model = args.model

    # Step 1: Tokenize
    tokens = tokenize(text, model)
    print(f"Tokenized: {tokens}")

    # Step 2: Generate one token
    output = generate_completion(text, model)

    # Step 3: Strip original input from output
    suggestion = output[len(text):].strip() if output.startswith(text) else output
    print(f"Suggestion: {suggestion}")

if __name__ == "__main__":
    main()
