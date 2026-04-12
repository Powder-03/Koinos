# Koinos - Dual-Mode Voice & Manual Expense Tracker (Powered by MCP)

Koinos is a modern, AI-powered "Dual-Mode" expense tracking backend application. It provides standard CRUD features for a frontend (e.g., an Android Kotlin app) alongside an advanced LangGraph-powered conversational agent. 

Crucially, Koinos leverages the **Model Context Protocol (MCP)** via `FastMCP` to securely and standardly expose our core Python database functions as AI-native tools. This allows the AI agent to log, search, update, and manage expenses using natural language, establishing a direct bridge between LLM reasoning and the underlying PostgreSQL database.

---

## 🌟 Product Vision & Features

1. **VOICE LOGGING:** Log an expense using natural language (e.g., *"Spent 500 on a cab"*).
2. **MANUAL MANAGEMENT:** Standard, robust CRUD endpoints for manual UI edits and swipe-to-delete functionalities.
3. **CONVERSATIONAL MEMORY:** The AI remembers context. If you say, *"Actually, make it 600"* right after logging a voice command, the AI understands which entry needs updating.
4. **DUAL SOURCE OF TRUTH (Via MCP):** The AI has direct access to queries (via FastMCP tools) allowing it to find and confirm existing records in real-time before making modifications.

---

## 🔌 The Power of Model Context Protocol (MCP)
By utilizing **FastMCP**, the AI agent isn't just generating text—it interacts with the application's true domain logic using standardized protocols:
* **Standardized Tooling:** The `add_expense`, `search_expenses`, `update_expense`, and `delete_expense` functions are exported using MCP, making them seamlessly available to the LangGraph/LangChain orchestrator.
* **Safety & Verification:** MCP allows the voice agent to dynamically query the database *before* making updates or deletions. The agent actively uses the `search_expenses` MCP tool to find the correct `expense_id`, eliminating hallucinated IDs and incorrect operations.

---

## 🛠 Tech Stack

* **API Gateway / Presentation:** FastAPI
* **AI Orchestrator:** LangGraph & LangChain
* **LLM Provider:** Groq (`llama-3.1-8b-instant`)
* **Database & ORM:** PostgreSQL + `asyncpg` + SQLAlchemy 2.0 (Async + Mapped strictly typed models)
* **AI Memory:** LangGraph `AsyncPostgresSaver` (Storing conversational checkpoints in Postgres)
* **Tools / Agent Extensibility:** Model Context Protocol (MCP) via FastMCP
* **Config Management:** `pydantic-settings`

---

## 📁 Architecture (Clean Architecture)

```text
src/
├── core/
│   └── config.py                   # Centralized Pydantic Settings
├── domain/
│   └── models.py                   # Pydantic Domain Models (Expense, ExpenseCategory)
├── application/
│   ├── interfaces/
│   │   └── repository.py           # Abstract Base Repository class
│   └── agent/
│       ├── graph.py                # LangGraph Orchestrator (ChatGroq + Tools)
│       └── state.py                # Agent State definition
├── infrastructure/
│   ├── database/
│   │   ├── connection.py           # Async SQLAlchemy Engine & SessionMaker
│   │   ├── models.py               # Declarative ORM Models
│   │   └── repository.py           # Postgres-specific Repository Implementation
│   └── mcp/
│       └── server.py               # FastMCP Server (AI Tools: add, search, update, delete)
└── presentation/
    ├── api/
    │   ├── manual_router.py        # Synchronous-feeling Standard CRUD Endpoints
    │   └── voice_router.py         # Voice/Text Endpoint dispatching to LangGraph
    └── main.py                     # FastAPI Application Factory & Lifespan
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.11+
- Docker & Docker Compose (Optional but recommended for Postges DB)

### 2. Environment Configuration
Clone the repository and set up the configuration file:
```bash
cp .env.example .env
```
Edit the `.env` file to insert your **Groq API Key**.

### 3. Running with Docker Compose
To easily spin up both the FastAPI application and the PostgreSQL database:
```bash
docker compose up --build
```

### 4. Running Locally (Without Dockerizing the app)
Start the database background:
```bash
docker compose up db -d
```

Install requirements and run via Uvicorn:
```bash
pip install -r requirements.txt
uvicorn src.presentation.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📡 API Endpoints

### 📱 **Manual Mode Endpoints (UI)**
- `POST /api/manual/`: Create an expense
- `GET /api/manual/`: Retrieve a list of expenses
- `PUT /api/manual/{expense_id}`: Update a specific expense
- `DELETE /api/manual/{expense_id}`: Remove an expense

### 🎙 **Voice Mode Endpoints (AI via LangGraph + MCP)**
- `POST /api/voice/`: Accepts a textual representation of voice commands (`{"message": "string", "user_id": "string"}`) and routes it through the LangGraph AI agent, empowered by our MCP server.

---

## 🔒 Category Validations
Categories are strictly typed to prevent LLM hallucinations:
- Food, Transport, Entertainment, Shopping, Utilities, Health, Other.
