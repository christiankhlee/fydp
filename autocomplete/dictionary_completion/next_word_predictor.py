import subprocess
import argparse
import json
import os



LLAMA_BIN = "../../llama.cpp/build/bin/llama-cli"
DEFAULT_MODEL = "../../llama.cpp/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"

print(f"Using LLM binary: {LLAMA_BIN}")
print("Using llama-cli at:", os.path.abspath(LLAMA_BIN))
def predict_next_word(prompt, model_path):
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
        "--no-conversation"
        # "-no-cnv"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout.strip()
        print("Raw model output:\n", output)

        if formatted_prompt in output:
            suffix = output.split(formatted_prompt, 1)[-1].strip()
        else:
            suffix = output.strip()

        tokens = suffix.split()
        predictions = []
        for token in tokens:
            cleaned = ''.join(c for c in token if c.isalpha()).lower()
            if cleaned and cleaned not in predictions:
                predictions.append(cleaned)
            if len(predictions) == 3:
                break

        return predictions if predictions else ["[No valid prediction]"]

    except Exception as e:
        return [f"[LLM Error: {e}]"]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="Text before the cursor")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Path to model")
    args = parser.parse_args()

    text = args.text.strip()
    model = args.model

    next_words = predict_next_word(text, model)
    result = {
        "next_word_prediction": next_words
    }

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
