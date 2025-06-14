import subprocess
import argparse
import json
from nltk.corpus import words
import nltk

# Ensure NLTK word list is downloaded
nltk.download('words', quiet=True)
word_set = set(w.lower() for w in words.words())

LLAMA_BIN = "../../llama.cpp/build/bin/llama-cli"
DEFAULT_MODEL = "../../llama.cpp/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"

print(f"Using LLM binary: {LLAMA_BIN}")

def predict_next_word(prompt, model_path):
    # Reformat prompt to encourage completion naturally
    formatted_prompt = f"Complete this sentence with one likely next word:\n{prompt.strip()}"

    cmd = [
        LLAMA_BIN,
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
        print("Raw model output:\n", output)

        # Strip everything before the prompt if echoed
        if formatted_prompt in output:
            suffix = output.split(formatted_prompt, 1)[-1].strip()
        else:
            suffix = output.strip()

        # Token filtering
        tokens = suffix.split()
        for token in tokens:
            cleaned = ''.join(c for c in token if c.isalpha()).lower()
            if cleaned in word_set:
                return [cleaned]

        # Fallback: return first alphabetic token if present
        for token in tokens:
            cleaned = ''.join(c for c in token if c.isalpha()).lower()
            if cleaned:
                return [cleaned]

        return ["[No valid prediction]"]
    except Exception as e:
        return [f"[LLM Error: {e}]"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="Text before the cursor")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Path to model")
    args = parser.parse_args()

    text = args.text.strip()
    model = args.model

    next_word = predict_next_word(text, model)

    result = {
        "next_word_prediction": next_word
    }

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
