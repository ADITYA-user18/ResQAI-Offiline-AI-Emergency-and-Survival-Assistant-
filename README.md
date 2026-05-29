<div align="center">
  <img src="./assets/logo.png" alt="ResQAI Logo" width="150"/>
  <h1>ResQAI 🛡️</h1>
  <p><strong>Fully Offline AI Emergency & Survival Assistant</strong></p>
  <p>ResQAI is a local-first, privacy-focused AI companion designed to provide critical first-aid, survival, and emergency response instructions—even when the power grid fails and the internet goes down.</p>
  <br />
</div>

<div align="center">
  <!-- TODO: Replace with actual screenshot links -->
<img width="1916" height="904" alt="image" src="https://github.com/user-attachments/assets/f9384372-2039-4abc-8bf0-38a026b48b70" />
</div>

---

## 🚀 Features

- **100% Offline Capable:** Runs entirely on your local machine using Ollama and local LLM models (TinyLlama/Phi3). No API keys, no internet requests, no data leaving your device.
- **RAG Knowledge Base:** Powered by a locally embedded FAISS vector store pre-loaded with critical First-Aid protocols, survival guides, and emergency response manuals.
- **Zero-Telemetry Privacy:** Isolated local SQLite database with bcrypt-encrypted passwords for user authentication and chat history.
- **Premium UI/UX:** Built with React, Tailwind v4, Framer Motion, and GSAP. Features a dynamic glassmorphism design, cyber-inspired color palette, and hardware-accelerated animations optimized for both desktop and mobile.
- **Network Exposable:** Built-in capability to securely expose the interface to your local LAN or via SSH tunnels for remote emergency access.

## 🛠️ Tech Stack

### Frontend (Web)
- **Framework:** React + Vite
- **Styling:** Tailwind CSS v4 + Vanilla CSS
- **Animations:** Framer Motion & GSAP
- **Routing:** React Router v6
- **Icons:** React Icons / Lucide React

### Backend (API & AI)
- **Framework:** FastAPI (Python)
- **AI Engine:** Ollama (Local inference)
- **Embeddings:** Nomic-Embed-Text + FAISS Vector Indexing
- **Database:** SQLite (local storage)
- **Auth:** JWT (JSON Web Tokens) with bcrypt password hashing

---

## ⚙️ Local Setup Instructions

### Prerequisites
1. **Node.js** (v18+)
2. **Python** (3.10+)
3. **[Ollama](https://ollama.ai/)** installed and running on your system.

### 1. Model Preparation
Before running the backend, pull the necessary models via Ollama:
```bash
# Pull the language model
ollama pull phi3  # or tinyllama

# Pull the embedding model (CRITICAL for RAG)
ollama pull nomic-embed-text
```

### 2. Backend Setup
Navigate to the `backend` directory and start the FastAPI server:
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt

# Start the backend server
python server.py
```
*(The backend runs on `http://127.0.0.1:8000`)*

### 3. Frontend Setup
In a new terminal window, navigate to the `web` directory:
```bash
cd web
npm install
npm run dev
```
*(The frontend runs on `http://localhost:5173`)*

---

## 📸 Screenshots

> **Note to developer:** *Place your stunning UI screenshots here! Save images to the `assets/` folder in the repository root and update the paths below.*

### Login / Authentication
<img width="1902" height="900" alt="image" src="https://github.com/user-attachments/assets/5211755b-a65c-4426-9365-0eb70d96b4ef" />


### Emergency Chat Interface
<img width="1918" height="904" alt="image" src="https://github.com/user-attachments/assets/a048115f-e2ba-42b1-80c5-211dc16eeb36" />




---

## 🔒 Security & Privacy Notice
ResQAI is designed as an offline-first tool. By design, no telemetry, analytical data, or chat histories are ever transmitted over the web. Ensure you keep your `.env` keys and `database/` folders out of version control.

---
*Built to keep you safe when everything else fails.*
