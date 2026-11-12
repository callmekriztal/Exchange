# The AI Economy — Autonomous Agent Marketplace

An autonomous marketplace where AI agents independently discover services, negotiate bilateral prices, purchase services, execute specialized tasks, and settle payments via PayPal Sandbox.

Human users submit high-level strategic objectives and budget constraints. AI agents handle the economic discovery and transactions within predefined spending policies and strict authorization boundaries.

---

## 1. Key Highlights & Security Architecture

- **Zero LLM Payment Access:** AI agents formulate structured economic proposals, but payment credentials, client secrets, and money movement remain strictly guarded in the backend security perimeter.
- **Human-in-the-Loop Authorization:** Before any funds move, the human user reviews the negotiated contracts and authorizes the checkout through the official PayPal JavaScript SDK modal.
- **Double-Entry Accounting Ledger:** Internal agent micro-credits, platform fees, and escrow holds are recorded in an immutable PostgreSQL double-entry ledger, cleanly decoupled from external PayPal fiat settlements.
- **4 Autonomous Agents:**
  - **Apex Buyer Agent:** Decomposes objectives into subtasks, queries registry, manages budget limits, and grades deliverable quality against rubrics.
  - **Veritas Research Agent:** Gathers empirical citations, primary evidence, and factual findings.
  - **QuantMatrix Analysis Agent:** Computes quantitative trajectories, CAGR percentages, and KPI modeling.
  - **Executive Brief Report Agent:** Synthesizes research and analytics into publication-grade executive markdown reports.
- **Alternating-Offer Negotiation Protocol:** Bounded multi-round negotiation with reservation prices and concession curves.
- **Real-Time WebSockets:** Live state transitions (decomposition, negotiation rounds, contracts, payment, execution, deliverable evaluation, ledger settlement) stream to the React UI.

---

## 2. Technology Stack

- **Frontend:** React 18, TypeScript, Tailwind CSS, Lucide Icons, `@paypal/react-paypal-js`.
- **Backend:** Python 3.11, FastAPI, SQLAlchemy 2.0 (asyncpg), Pydantic v2.
- **Database:** PostgreSQL 16.
- **AI Orchestration:** LangGraph StateGraph, OpenAI Structured Outputs (`response_format`).
- **Payments:** PayPal Orders API v2 (Sandbox environment) with OAuth2 token manager, idempotent captures, and webhook verification.
- **Realtime:** FastAPI WebSockets.
- **Deployment:** Docker Compose.

---

## 3. Quickstart with Docker Compose

### Prerequisites
- Docker (20.10+) and Docker Compose (v2.0+)

### 1. Clone & Configure Environment
```bash
cp .env.example .env
```
*(The repository includes a ready-to-use default `.env` configured for Sandbox and local containers)*.

### 2. Start the Stack
```bash
docker compose up -d --build
```
This spins up:
- **PostgreSQL Database** (`ai_economy_db`) on internal port `5432` (host port `5433`).
- **FastAPI Backend** (`ai_economy_backend`) on `http://localhost:8000` (OpenAPI docs at `http://localhost:8000/docs`).
- **React Frontend** (`ai_economy_frontend`) on `http://localhost:5173`.

### 3. Initialize Database Tables
```bash
docker compose run --rm backend python app/db/init_db.py
```

### 4. Seed the Agent Marketplace & Demo Data
```bash
docker compose run --rm backend python app/db/seed_demo.py
```

Now open **`http://localhost:5173`** in your browser to view the interactive dashboard, live trades, agent catalog, and the accounting ledger.

---

## 4. Running Automated Tests

Run the complete end-to-end integration test suite inside the container:
```bash
docker compose run --rm backend pytest tests/test_e2e_workflow.py -v -s
```

The test validates:
1. Health check & user authentication (JWT).
2. Seeding of the 4 autonomous agents.
3. Objective submission with maximum budget limits.
4. LangGraph goal decomposition into sequential subtasks.
5. Marketplace discovery & seller matchmaking.
6. Multi-agent alternating-offer price negotiation.
7. Contract generation with immutable cryptographic terms.
8. PayPal Orders API v2 order creation (`intent: CAPTURE`).
9. PayPal capture and escrow lock in the internal ledger.
10. Seller execution producing verified artifacts (SHA-256).
11. Buyer Agent quality evaluation (completeness, rigor, formatting).
12. Escrow settlement to seller agent balance and marketplace platform fee.

---

## 5. Architectural Documentation

Comprehensive architectural blueprints and specifications are documented under `docs/`:
- [`docs/README.md`](./docs/README.md): Documentation index.
- [`docs/architecture.md`](./docs/architecture.md): Authoritative architectural specification:
  - System architecture and security principles.
  - Mermaid component interaction sequence diagram.
  - Mermaid database entity relationship diagram (ERD).
  - PostgreSQL schema DDL with check constraints and enums.
  - REST & WebSocket API specification.
  - AI agent interaction workflow & LangGraph StateGraph.
  - PayPal payment lifecycle & webhook signature verification.
  - Project directory structure.
  - Environment variables reference.
  - 18 implementation prompts breakdown.

---

## 6. License
MIT License.
