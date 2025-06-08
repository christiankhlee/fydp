import nltk
import sys

# Download word list if not already present
try:
    from nltk.corpus import words
except LookupError:
    nltk.download('words')
    from nltk.corpus import words

def suggest_completions(prefix, max_suggestions=10):
    vocab = set(w.lower() for w in words.words())
    prefix = prefix.lower()

    # Only suggest words that start with the prefix
    matches = sorted([w for w in vocab if w.startswith(prefix)])

    return matches[:max_suggestions]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 complete_word.py <partial_word>")
        sys.exit(1)

    prefix = sys.argv[1]
    suggestions = suggest_completions(prefix)

    print(f"Suggestions for '{prefix}':")
    for word in suggestions:
        print(f"- {word}")
