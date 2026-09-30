# AgentDesk AI — Multi-Agent Helpdesk / Ticket Triage

## Purpose
Automates IT/support ticket triage: intake -> classify & prioritize -> answer from the internal knowledge base (with cited sources) -> auto-resolve simple cases or escalate to a human. Destructive or irreversible actions (e.g. account deletion, password reset, access revocation) always require human approval.

## Tech Stack
- **API:** Python, FastAPI, JWT auth (short-lived access token + refresh endpoint), webhook endpoint for ticket intake
- **Orchestration:** **LangGraph** (chosen over plain LangChain: the pipeline is a stateful graph with a conditional branch and a human-approval pause/resume, which LangGraph models natively). LangChain is used for model wrappers, tools, and retrievers.
- **LLMs:** Gemini `gemini-2.5-flash` (primary), Mistral (fallback only)
- **Tools:** real LangChain tool calling; actions exposed via an MCP server
- **Vector store:** FAISS (primary), Chroma (alternative, switched by `VECTOR_STORE`)
- **DB:** PostgreSQL via SQLAlchemy (tickets, agent actions, audit trail)
- **UI:** Streamlit multi-page app
- **Tests:** pytest

## Architecture
```
Webhook / Streamlit form -> validation -> tickets table
   -> LangGraph pipeline:
      classify_node -> kb_node (RAG) -> action_node -> [approval gate] -> execute via MCP
```
- **Classification agent:** category + priority as structured output (Gemini).
- **Knowledge-base agent:** retrieves from FAISS/Chroma over docs and past resolved tickets; answer must include source IDs.
- **Action agent:** chooses a tool (`lookup_ticket`, `update_ticket`, `escalate`, `reset_password`, ...) via tool calling. Non-destructive tools (`lookup_ticket`, `update_ticket`, `escalate`) run through the MCP server; destructive tools are deliberately not exposed over MCP and run in-process behind the approval gate.
- **Approval gate:** tools are tagged `destructive`. Destructive calls create a `pending_approval` record and the graph stops. Only an authenticated human approving via API/dashboard resumes it. The executor re-checks approval status itself (defense in depth).
- **Audit-first rule:** an audit row (`status=started`) is written *before* every action/tool call, then updated to `succeeded`/`failed`.

## Model Routing, Retry, Fallback
- One entry point (`llm/router.py`) for every LLM call.
- Single-model features (classification, RAG, action reasoning) use **Gemini only**. Features needing multiple models use Gemini **and** Mistral together.
- Per-model call: explicit timeout, up to **3 attempts** with exponential backoff (+ jitter).
- Mistral is called **only** if Gemini exhausts retries (error, timeout, rate limit). If Mistral also fails, a typed `LLMUnavailableError` is raised and the ticket is marked `needs_human`.
- Every call records tokens and estimated cost (`llm/usage.py`); a per-ticket summary is logged and stored.

## Logging & Security
- Structured JSON logs (INFO/WARNING/ERROR) for each agent decision and tool call: decision + reasoning summary, ticket ID, never raw ticket body.
- Secrets come only from `.env` via `pydantic-settings`; never hardcoded or logged. `.env` is git-ignored; `.env.example` is committed.
- Every external call (LLM, MCP, DB) has a timeout and error handling; failures are logged, audited, and surfaced — never silent.

## Code Style (strict)
- Every file stays under ~200 words of code; split into a new module and import when exceeded.
- Short, clearly named functions; no deep nesting; readability over cleverness.
- One-line comments only where the "why" is non-obvious.

## Evaluation Pipeline
`evals/dataset.jsonl` holds labeled tickets. `python -m evals.run` runs the classifier over them, reports accuracy and per-category confusion, saves timestamped results to `evals/results/`, and exits non-zero below `EVAL_MIN_ACCURACY`. Run it after every change (also wired into CI/pytest marker `eval`).

## Required Tests
Classifier logic; Gemini->Mistral fallback (mocked Gemini failure); approval gate (destructive action never runs unapproved); one full pipeline integration test.
