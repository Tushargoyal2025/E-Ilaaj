<div align="center">

# 🩺 E-Ilaaj
### AI-Powered Homeopathic Consultation Chatbot

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![LangChain](https://img.shields.io/badge/LangChain-AI-green)
![ChromaDB](https://img.shields.io/badge/ChromaDB-VectorDB-orange)
![Groq](https://img.shields.io/badge/Groq-LLM-purple)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

An AI-guided homeopathic case-taking chatbot, grounded in the **complete Kent's Repertory of the Homeopathic Materia Medica** (1,366 pages) via Retrieval-Augmented Generation (RAG). It holds a real case-taking conversation — one clarifying question at a time — then produces a structured consultation report.

</div>

---

# 📌 Table of Contents

- Overview
- Features
- System Architecture
- Tech Stack
- Project Workflow
- Folder Structure
- Database Design
- API Endpoints
- Installation
- Performance Notes
- Future Scope
- Medical Disclaimer
- Contributors

---

# 📖 Overview

E-Ilaaj combines a classical homeopathic reference text (Kent's Repertory, fully ingested — ~9,200 chunks across the entire book), a RAG pipeline, and an LLM to hold a real case-taking conversation with a user — asking the same kind of clarifying questions a homeopath would (duration, severity, what makes it better or worse) — before producing a final, structured consultation report.

Every consultation is saved per-user and per-session (`conversation_id`), so users can start a new consultation at any time and revisit past ones from the sidebar — just like a real chat product.

---

# ✨ Features

- 🔐 JWT-based authentication (signup/login, bcrypt-hashed passwords, secrets loaded from `.env`)
- 💬 Real-time chat interface with a persistent session per consultation
- ⌨️ Animated typing indicator while the AI is generating a reply
- 🧠 Retrieval-Augmented Generation over the **complete** Kent's Repertory (ChromaDB + HuggingFace embeddings)
- 🤖 Conversational case-taking — one clarifying question at a time, never a wall of text
- 📋 Automatic structured report after enough case details are gathered: **Disease Overview, Indicated Remedy, Daily Routine, Diet**
- 🗂 Multiple consultations per user, browsable and switchable from the sidebar ("Recent")
- 🎬 Animated splash screen → login/signup → chat, all served from one FastAPI app
- ⚠️ Persistent (non-intrusive) medical safety notice in the UI, instead of repeated in-chat disclaimers
- ⚡ Cached embedding/LLM clients (loaded once per process, not once per message) for fast responses
- 🛠 Dev server (`run.py`) that only restarts on actual code changes — not on database/vector-store writes

---

# 🏗 System Architecture

```
                    User
                     │
                     ▼
         index.html (splash animation)
                     │
                     ▼
        auth.html (Login / Sign Up) ──► POST /signup, /login
                     │
                     ▼
              chat.html (chat UI)
                     │
                     ▼
              FastAPI Backend (main.py)
                     │
        ┌────────────┼─────────────┐
        ▼            ▼             ▼
   database.py   routers/auth.py  routers/chat.py
   (SQLite:           │                 │
   users +            │                 ▼
   chat_messages,     │          eilaaj/pipeline.py
   per conversation)  │                 │
                       │      ┌──────────┴──────────┐
                       │      ▼                      ▼
                       │  vector_store.py       llm.py (Groq,
                       │  (ChromaDB retrieval,   cached client)
                       │   cached, full book)          │
                       │      │                       │
                       │      └───────────┬───────────┘
                       │                  ▼
                       │        Conversational reply, or
                       │        structured report after
                       │        4+ user turns
                       ▼                  │
                  JWT session        saved back to
                                     chat_messages
```

---

# ⚙ Tech Stack

| Category | Technology |
|-----------|------------|
| Frontend | HTML, CSS, vanilla JavaScript (no framework) |
| Backend | FastAPI |
| Language | Python 3.11+ |
| Database | SQLite |
| Vector Database | ChromaDB (full Kent's Repertory ingested, ~9,200 chunks) |
| Embeddings | HuggingFace (`all-MiniLM-L6-v2`), cached per process |
| AI Framework | LangChain |
| AI Technique | Retrieval-Augmented Generation (RAG) |
| LLM | Groq (`llama-3.3-70b-versatile`) |
| Auth | JWT (PyJWT) + bcrypt |
| Version Control | Git & GitHub |

---

# 🔄 Project Workflow

```
User opens the site (index.html splash)
          ↓
Login / Sign Up (auth.html → /signup or /login)
          ↓
JWT stored client-side, redirected to chat.html
          ↓
User describes a symptom (typing indicator shows while waiting)
          ↓
Backend fetches this conversation's prior history (SQLite, by conversation_id)
          ↓
ChromaDB retrieves matching rubrics from the full Kent's Repertory
          ↓
Groq LLM generates a short, one-question-at-a-time reply
          ↓
(after ~4 user messages in this conversation)
          ↓
LLM switches to report mode:
  • Disease Overview
  • Indicated Remedy
  • Daily Routine
  • Diet
          ↓
Report shown in chat, saved to history.
User can start a "New Consultation" anytime — a fresh conversation_id,
previous ones stay browsable in the sidebar.
```

---

# 🗂 Folder Structure

```
E-Ilaaj/
├── main.py                 # FastAPI app entrypoint — mounts routers + serves static/
├── run.py                    # Dev server — reloads only on .py file changes
├── ingest.py                  # CLI: build the vector store from data/
├── database.py                 # SQLite: users, chat history (per conversation), password hashing, JWT
├── deps.py                      # FastAPI dependency: get current user from Bearer token
├── requirements.txt
├── .env.example
├── .gitignore
│
├── eilaaj/                      # Core AI package — one responsibility per file
│   ├── config.py                  # paths, model names, chunk size, prompt templates, report trigger
│   ├── document_loader.py          # load PDFs/TXTs from data/
│   ├── splitter.py                  # chunk documents
│   ├── embeddings.py                 # embedding model factory (cached)
│   ├── vector_store.py                # build/save/load Chroma + retriever (cached)
│   ├── llm.py                          # Groq LLM factory (cached)
│   └── pipeline.py                      # orchestrates ingestion + query_rag() + report-mode switch
│
├── routers/
│   ├── auth.py                  # POST /signup, POST /login
│   └── chat.py                   # POST /chat/, GET /chat/history, GET /chat/conversations
│
├── data/                          # source PDFs/TXTs (Kent's Repertory, etc.) — ingest.py reads this
│
└── static/                         # frontend, served directly by FastAPI
    ├── index.html                    # splash / animated intro → auth.html
    ├── auth.html                      # login / signup → chat.html
    ├── chat.html                       # the consultation UI (auth-guarded)
    ├── css/styles.css
    └── js/
        ├── auth.js
        └── chat.js                       # typing indicator, conversation switching, history list
```

---

# 🗄 Database Design

## SQLite (`user.db`)

**`users`**
| Column | Type |
|---|---|
| id | INTEGER PK |
| name | TEXT |
| email | TEXT UNIQUE |
| password | TEXT (bcrypt hash) |

**`chat_messages`**
| Column | Type |
|---|---|
| id | INTEGER PK |
| user_email | TEXT |
| conversation_id | TEXT — groups messages into separate consultations |
| sender | TEXT (`user` / `bot`) |
| message | TEXT |
| timestamp | DATETIME |

## ChromaDB (`chroma_db/`)

Vector embeddings of the **entire** Kent's Repertory (rubric text → remedy lists), built by `ingest.py` — ~9,200 chunks covering the full 1,366-page book.

---

# 🌐 API Endpoints

| Method | Endpoint | Description |
|----------|----------|------------|
| POST | `/signup` | Register a new user |
| POST | `/login` | Log in, returns a JWT |
| POST | `/chat/` | Send a message in a conversation, get an AI reply |
| GET | `/chat/history?conversation_id=` | Get message history for one conversation |
| GET | `/chat/conversations` | List a user's past consultations (for the sidebar) |

All `/chat/*` endpoints require `Authorization: Bearer <token>`.

---

# 🚀 Installation

```bash
git clone https://github.com/Tushargoyal2025/E-Ilaaj.git
cd E-Ilaaj
```

**Create and activate a virtual environment**

```bash
python -m venv .venv
```

Windows: `.venv\Scripts\activate`
Linux / Mac: `source .venv/bin/activate`

**Install dependencies**

```bash
pip install -r requirements.txt
```

**Set up environment variables**

```bash
cp .env.example .env
```

Then edit `.env`:
```
GROQ_API_KEY=your-groq-api-key-here
SECRET_KEY=your-long-random-secret-key-here
```
Generate a secure `SECRET_KEY`:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Build the knowledge base**

Put your source documents (e.g. Kent's Repertory) in `data/`, then:

```bash
python ingest.py
```

**Run the app**

```bash
python run.py
```

Visit `http://127.0.0.1:8000/` — splash screen → sign in / sign up → chat.

---

# ⚡ Performance Notes

- Embedding model, vector store, and LLM client are all **cached per process** (`@lru_cache`) — they load once, not on every message.
- Initial server startup takes longer (loading `torch`/`transformers`/`chromadb`) — this is expected for local embedding models, not a bug.
- Use `python run.py` instead of `uvicorn main:app --reload` directly — it's configured to reload **only** on `.py` file changes, so chat activity (which writes to the database) never triggers an unnecessary restart.

---

# 🎯 Future Scope

- 🎤 Voice-based consultation
- 📱 Mobile application
- 📄 Exportable PDF consultation reports
- 👨‍⚕ Practitioner review / handoff dashboard
- 🌍 Multi-language support
- ☁ Cloud deployment

---

# ⚠ Medical Disclaimer

E-Ilaaj references Kent's Repertory of the Homeopathic Materia Medica (1897, public domain). Its responses:

- Are **not a medical diagnosis**
- Should **not replace professional healthcare advice**
- Should always be verified by a qualified physician or homeopath

If symptoms are severe, worsening, or life-threatening, users should seek immediate care from a licensed doctor or emergency medical service.

---

# 👨‍💻 Contributors

**Team E-Ilaaj**

Built with Python, FastAPI, LangChain, ChromaDB, Groq, SQLite, HTML, CSS, and JavaScript.

---

<div align="center">

### ⭐ If you like this project, don't forget to star the repository!

</div>