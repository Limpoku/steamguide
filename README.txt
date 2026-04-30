# 🎮 SteamGuide Assistant

AI-powered Steam game recommender with interactive UI, prices, ratings, and clickable game cards.

---

## 🚀 Requirements

* Python **3.10+** (recommended: 3.13.7)
* Ollama installed and running
* Internet connection (Steam API)

---

## 📦 Installation

1. Clone the repository or download the project.

2. Install dependencies:

```bash
pip install -r requirements.txt
```
---

## ⚙️ Setup

### 1. Start Ollama

Before running the app, start Ollama:

```bash
ollama serve
```

(Optional: download model if not installed)

```bash
ollama pull llama3
```

---

### 2. Run the application

```bash
python app.py
```

---

## 🌐 Access the App

Open in your browser:

```
http://localhost:7860
```

---

## ✨ Features

* 🔎 Search for any game (e.g. *Albion Online*)
* 🤖 AI-powered recommendations
* 💰 Steam prices (multi-currency support)
* 🔻 Discounts and original prices
* ⭐ Ratings (Very Positive, etc.)
* 🏷️ Game genres/tags
* 🖱️ Clickable cards → open Steam page

---

## 📁 Project Structure

```
STEAMGUIDE/
│
├── app.py              # App entry point
├── ui.py               # Gradio UI (cards, layout)
├── steam_api.py        # Steam API logic (search + details)
├── agente_assist.py    # AI agent logic
├── tools.py            # Tools used by the agent
├── db.py               # Database handling
├── requirements.txt
├── __pycache__/        # Python cache (auto-generated)
```

---

## ⚠️ Notes

* Prices come from the Steam API and may vary by region.
* Some games may not include ratings or price data.
* App performance depends on API response time.

---

## 👨‍💻 Author

Francisco — AI Engineer Student
