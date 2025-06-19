#!/usr/bin/env python3
"""
Test script to verify LLM setup and functionality
"""
import subprocess
import os

def test_llm_setup():
    # Test paths
    llama_bin = "../../llama.cpp/build/bin/llama-cli"
    model_path = "../../llama.cpp/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    
    print("=== LLM Setup Test ===")
    print(f"Checking llama-cli at: {llama_bin}")
    print(f"Exists: {os.path.exists(llama_bin)}")
    
    print(f"\nChecking model at: {model_path}")
    print(f"Exists: {os.path.exists(model_path)}")
    
    if not os.path.exists(llama_bin):
        print("\n❌ llama-cli not found!")
        print("Make sure you've built llama.cpp and the path is correct")
        return False
        
    if not os.path.exists(model_path):
        print("\n❌ Model file not found!")
        print("Make sure you've downloaded the model and the path is correct")
        return False
    
    print("\n✅ Both files exist, testing LLM call...")
    return test_llm_call(llama_bin, model_path)

def test_llm_call(llama_bin, model_path):
    test_prompt = "The weather today is"
    formatted_prompt = f"Complete this sentence with the next word: {test_prompt}"
    
    cmd = [
        llama_bin,
        "-m", model_path,
        "--prompt", formatted_prompt,
        "--n-predict", "5",
        "--temp", "0.8",
        "--top-k", "40",
        "--top-p", "0.9",
        "--repeat-penalty", "1.1",
        "--no-cnv"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        print(f"\nReturn code: {result.returncode}")
        print(f"Stdout: {repr(result.stdout)}")
        print(f"Stderr: {repr(result.stderr)}")
        
        if result.returncode == 0:
            print("\n✅ LLM call successful!")
            return True
        else:
            print(f"\n❌ LLM call failed with return code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n❌ LLM call timed out")
        return False
    except Exception as e:
        print(f"\n❌ LLM call failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_llm_setup()
    if success:
        print("\n🎉 LLM setup is working correctly!")
    else:
        print("\n💔 LLM setup needs fixing before the predictions will work")