import os
import argparse
import json

# Load common words and frequencies from file using an absolute path
def load_common_words(path=None, min_freq=1000):
    if path is None:
        # This resolves the path relative to this script's location
        path = os.path.join(os.path.dirname(__file__), "common1.txt")

    word_freq = []
    with open(path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                word, freq = parts
                if word.isalpha() and int(freq) >= min_freq:
                    word_freq.append((word.lower(), int(freq)))
    return word_freq

# Load the word list once
word_list = load_common_words()

def complete_word(prefix, limit=5):
    prefix = prefix.lower()
    matches = [word for word, _ in word_list if word.startswith(prefix)]
    return matches[:limit]

def predict_next_word(text: str) -> str:
    words_in_text = text.strip().split()
    last_word = words_in_text[-1] if words_in_text else ""
    prefix = last_word if last_word.isalpha() else ""
    completions = complete_word(prefix) if prefix else []
    return completions[0] if completions else ""

# For CLI usage (optional, useful for debugging)

def get_predictions(text: str, limit=3) -> list[str]:
    words = text.strip().split()
    last = words[-1] if words else ""
    prefix = last.lower() if last.isalpha() else ""
    return complete_word(prefix, limit) if prefix else []

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="Text before the cursor")
    args = parser.parse_args()

    result = {
        "word_completions": complete_word(args.text)
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
