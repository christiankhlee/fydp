import subprocess

prompt = "Complete this sentence with likely next words:\nThe sun is"
cmd = [
    "/Users/christian/Documents/fydp/llama.cpp/build/bin/llama-cli",
    "-m", "/Users/christian/Documents/fydp/llama.cpp/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
    "--prompt", prompt,
    "--n-predict", "20",
    "--temp", "0.7",
    "--top-k", "40",
    "--top-p", "0.95",
    "--repeat-penalty", "1.1",
    "--no-conversation"
]

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    print("=== STDOUT ===")
    print(result.stdout)
    print("=== STDERR ===")
    print(result.stderr)
except Exception as e:
    print("Error:", e)
