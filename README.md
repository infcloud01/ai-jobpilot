# AI-JobPilot: Autonomous Multi-Agent Job Search Pipeline

AI-JobPilot is a production-ready, multi-tenant AI agent framework designed to systematically aggregate, evaluate, and strategize engineering job hunts. Driven by an autonomous **LangGraph** backend state machine and powered by OpenAI models, the system ingests data simultaneously across public marketplaces and private communication channels to generate hyper-personalized technical gap analyses and actionable career roadmaps.

---

## 🏗️ System Architecture

The application bifurcates its operations into two isolated channels: the user identification boundary (Identity Layer) and the autonomous data collection worker (Service Layer). This architecture prevents cross-tenant data contamination and establishes secure sandboxing for all user states.

---

## ⚡ Core Features Implemented So Far

1. **Secure Frontend Multi-Tenancy (Identity Layer)**: Integrated Google Identity Services SDK on the UI. Authenticated users generate a temporary, cryptographically encrypted Identity Token (JWT) transmitted securely via HTTP authorization headers.
2. **Dynamic State-Channel Architecture**: Configured a strict `JobHuntState` schema inside LangGraph to natively whitelist and route user query contexts (`query: str`), eliminating static, hardcoded role assumptions.
3. **Dual-Stream Scout Node Ingestion**:
   * **Live Public Market Sweep**: Automated HTTP requests to the **Adzuna REST API** to harvest real-world engineering vacancies matching user keywords dynamically.
   * **Live Personal Inbox Sync**: Connected to the secure **Gmail API** using an OAuth 2.0 Desktop app handshake. It scans the user's live mailbox for the past 7 days using high-intent recruiter queries (`"recruiter" OR "job application" OR "interview offer"`), automatically refreshing tokens via local `token.json` loops.
4. **Multipart Form Memory Streaming**: Implemented a streaming file uploader that catches raw `.txt` resume binaries over multipart/form-data vectors. FastAPI decodes the stream directly into temporary memory channels, eliminating the security and privacy risks of local disk state retention.
5. **Session Checkpoint Isolation**: Configured a `MemorySaver` mechanism that relies on the unique Google User UUID (`thread_id`) to cleanly partition memory banks, rendering the agent fully multi-tenant safe.

---

## 📂 Project Directory Structure

```text
ai-jobpilot/
├── .gitignore              # Global git rule exclusion matrix (venv, keys, caches)
├── README.md               # Documentation shell
├── frontend/
│   ├── index.html          # Utility-styled Tailwind interface view layer
│   └── app.js              # State controller, OAuth engine, and form streaming client
└── backend/
    ├── .env                # EXCLUDED FROM GIT - Houses private API keys
    ├── credentials.json    # EXCLUDED FROM GIT - Google Cloud Client credentials
    ├── token.json          # EXCLUDED FROM GIT - Automatically generated Google Refresh Token
    ├── test_agent.py       # Standalone terminal simulation script for testing graph nodes
    └── app/
        ├── __init__.py
        ├── main.py         # FastAPI application router, middleware, and form gateways
        ├── auth.py         # Google JWT cryptographic signature validation layers
        └── agent/
            ├── __init__.py
            ├── graph.py    # Main LangGraph flow compiler and memory weaver
            ├── state.py    # Strict structural schema definition class fields
            ├── nodes/
            │   ├── __init__.py
            │   ├── scout.py     # Aggregates Adzuna and Gmail data channels
            │   └── analyst.py   # Computes semantic evaluation matches via OpenAI LLM
            └── tools/
                ├── __init__.py
                ├── gmail.py     # Establishes live OAuth loop & reads inbox text snippets
                └── job_board.py # Communicates with live Adzuna REST endpoints
```

## 🚀 Step-by-Step Local Deployment Setup
1. Repository Safety Check
Ensure your absolute root directory has a .gitignore configured to guarantee security credentials never leak to public repositories:

```text
.venv/
backend/.env
credentials.json
token.json
__pycache__/
```

2. Configure Backend Credentials
Navigate to your backend/ directory, create a .env file, and plug in your live tokens:

```Bash
cd backend
touch .env
Populate .env with:
```

```text
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
OPENAI_API_KEY=your_openai_api_key
Place your downloaded Google Cloud Desktop application credential file straight into backend/credentials.json.
```
3. Initialize Python Environment
Install the full-stack dependency stack inside a clean virtual environment:

```Bash
# Spin up environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac/WSL
.venv\Scripts\activate     # Windows PowerShell
```

```bash
# Install package definitions
pip install fastapi uvicorn requests python-multipart python-dotenv langgraph langchain-openai google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

4. Configure Frontend Client ID

```bash
Open frontend/app.js and locate line 9 inside the window.onload block. Swap the placeholder string with your official Google Cloud Web Application Client ID:
client_id: "YOUR_WEB_APPLICATION_CLIENT_ID.apps.googleusercontent.com",
```


5. Launch the Local Architecture Suite
```bash
Boot the FastAPI Gateway Server (Port 8000):
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Boot the UI Display Web Server (Port 3000):
Open a second isolated terminal window, navigate to the project directory, and run:
```

```Bash
cd frontend
python3 -m http.server 3000
Open your browser to http://localhost:3000, log in using the official Google sign-in button, upload your text-based resume file, input a specific search keyword, and hit Launch Scout & Analysis Graph to witness the live execution trace!
```

## 🔮 Next Roadmap Milestones

Phase 6: Binary Parser Upgrade: Integrate pypdf or pdfplumber components into the file streaming engine to accept native .pdf resume uploads directly from desktops.

Phase 7: Cloud State Persistence Layer: Replace temporary in-memory MemorySaver setups with an asynchronous Amazon DynamoDB NoSQL storage cluster using Infrastructure as Code (Terraform).
