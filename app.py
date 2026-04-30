from ui import build_ui
import requests

def check_ollama():
    try:
        requests.get("http://localhost:11434")
    except:
        print("Run: ollama serve")
        exit()

if __name__ == "__main__":
    print("🎮 Steam UI running...")
    print("🌐 http://localhost:7860")

    build_ui()


    