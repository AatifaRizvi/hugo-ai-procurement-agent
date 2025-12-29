import subprocess
import time
from pyngrok import ngrok

# ------------------------------
# CONFIG
STREAMLIT_APP = "app.py"        # Tumhara Streamlit file
OLLAMA_MODEL = "gemma3:4b"      # Ollama model
STREAMLIT_PORT = 8501
# ------------------------------

def start_ollama():
    print("[1/3] Starting Ollama daemon...")
    return subprocess.Popen(
        ["ollama", "run", OLLAMA_MODEL],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def start_streamlit():
    print("[2/3] Starting Streamlit app...")
    return subprocess.Popen(
        ["streamlit", "run", STREAMLIT_APP],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def start_ngrok():
    print("[3/3] Starting Ngrok tunnel...")
    public_url = ngrok.connect(STREAMLIT_PORT)
    print(f"\n🚀 Your public Streamlit + Ollama URL is: {public_url}\n")
    return public_url

def main():
    ollama_proc = start_ollama()
    time.sleep(5)  # wait for Ollama daemon

    streamlit_proc = start_streamlit()
    time.sleep(3)  # wait for Streamlit server

    public_url = start_ngrok()
    print("Your Hugo AI demo is live!")
    print("Press Ctrl+C to stop all processes.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping all processes...")
        ollama_proc.terminate()
        streamlit_proc.terminate()
        ngrok.disconnect(public_url)
        print("All stopped. Bye!")

if __name__ == "__main__":
    main()
