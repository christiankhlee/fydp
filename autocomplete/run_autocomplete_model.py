import subprocess
import sys
import json
import argparse

def get_completion(text_before_cursor, model_path):
    args = [
        "../llama.cpp/build/bin/llama-cli",
        "-m", model_path,
        "--prompt", text_before_cursor,
        "--n-predict", "1",
        "--temp", "0.2",
        "--top-k", "10",
        "--top-p", "0.95",
        "--repeat-penalty", "1.1",
        "-no-cnv"
    ]

    try:
        result = subprocess.run(args, capture_output=True, text=True)
        output = result.stdout
    except Exception as e:
        return f"[Error running llama-cli: {e}]"

    lines = output.strip().split("\n")
    for line in lines:
        if line.strip().startswith(text_before_cursor.strip()):
            suggestion = line.strip()[len(text_before_cursor):].strip()
            return suggestion

    return "[No suggestion found]"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="Text before cursor")
    parser.add_argument("--model", required=True, help="Path to GGUF model")
    args = parser.parse_args()

    suggestion = get_completion(args.text, args.model)
    print(suggestion)

