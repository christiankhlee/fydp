import subprocess
import sys
import json
import re

def get_completion(text_before_cursor, n_predict=5):
    args = [
        "../llama.cpp/build/bin/llama-cli",
        "-m", "../llama.cpp/models/TinyLlama-1.1B-Chat-v1.0.Q4_K_M.gguf",
        "--prompt", text_before_cursor,
        "--n-predict", str(n_predict),
        "--temp", "0.2",
        "--top-k", "10",
        "--top-p", "0.95",
        "--repeat-penalty", "1.1",
        "-no-cnv"
    ]

    try:
        result = subprocess.run(args, capture_output=True, text=True)
        output = result.stdout.strip()
    except Exception as e:
        return f"[Error running llama-cli: {e}]", []

    # Get only the generated part
    if output.startswith(text_before_cursor):
        completion = output[len(text_before_cursor):].strip()
    else:
        completion = output.strip()

    return completion, output.split()

def suggest(text):
    if text.endswith(" "):
        # Suggest next words
        suggestion, _ = get_completion(text)
        next_words = suggestion.split()
        return {
            "type": "next-word",
            "suggestions": next_words[:3]
        }
    else:
        # Autocomplete current word
        prefix = re.split(r'\s+', text)[-1]
        prompt = text  # No formatting
        suggestion, _ = get_completion(prompt)
        completions = suggestion.split()
        candidates = [w for w in completions if w.startswith(prefix) and w != prefix]
        return {
            "type": "autocomplete",
            "prefix": prefix,
            "suggestions": candidates[:3]
        }

if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else ""

    result = suggest(text)

    if result["type"] == "autocomplete":
        print(f"Autocomplete (last word = '{result['prefix']}'): {result['suggestions']}")
    else:
        print(f"Next word suggestions: {result['suggestions']}")
