import argparse
import json

# Load common words and frequencies
def load_common_words(path="common1.txt", min_freq=1000):
    word_freq = []
    with open(path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                word, freq = parts
                if word.isalpha() and int(freq) >= min_freq:
                    word_freq.append((word.lower(), int(freq)))
    return word_freq

word_list = load_common_words()

def complete_word(prefix, limit=5):
    prefix = prefix.lower()
    matches = [word for word, _ in word_list if word.startswith(prefix)]
    return matches[:limit]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="Text before the cursor")
    args = parser.parse_args()

    text = args.text.strip()
    words_in_text = text.split()
    last_word = words_in_text[-1] if words_in_text else ""
    prefix = last_word if last_word.isalpha() else ""

    word_completions = complete_word(prefix) if prefix else []

    result = {
        "word_completions": word_completions
    }

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
