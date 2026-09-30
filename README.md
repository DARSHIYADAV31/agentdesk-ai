# AgentDesk AI

A multi-agent helpdesk. Employees raise tickets; AI agents classify them, look up a fix in the
knowledge base (with cited sources), and either resolve them or escalate to a human. Risky
actions (password reset, account deletion) always wait for an admin's approval.

**Stack:** FastAPI, JWT auth, LangGraph, Gemini 2.5 Flash (Mistral as fallback), FAISS / Chroma,
MCP, PostgreSQL (SQLAlchemy), Streamlit, pytest. Architecture details are in `CLAUDE.md`.

## Roles
| Role | Can do |
|---|---|
| Employee | Raise tickets, see only their own |
| Admin | See all tickets, assign, add internal notes, resolve, approve risky actions |
| Assignee | Work tickets the admin assigned: notes and mark resolved |

## Setup
Requires Python 3.11+, PostgreSQL 14+, and a Gemini API key.
```
python -m venv myenv
myenv\Scripts\activate            # Mac/Linux: source myenv/bin/activate
pip install -r requirements.txt
copy .env.example .env            # Mac/Linux: cp .env.example .env
```
Create a database named `agentdesk`, then fill in `.env` (API keys, `DATABASE_URL`, and random
values for `JWT_SECRET` and `WEBHOOK_SECRET`; generate them with
`python -c "import secrets;print(secrets.token_urlsafe(48))"`).

## Run
```
cd backend
python -m app.db.create_user admin admin     # prompts for the admin password
python -m app.rag.ingest                     # builds the search index from knowledge_base/
python -m app.db.seed_demo                   # optional demo tickets
uvicorn app.main:app --port 8000
```
In a second terminal:
```
cd frontend
streamlit run app.py                         # http://localhost:8501
```

## Test and evaluate
```
pytest                                       # no API keys or database needed
cd backend && python -m evals.run            # classification accuracy (needs a Gemini key)
```

## Notes
- The knowledge base (`backend/knowledge_base/`) holds sample articles only. Add your own `.md`
  files and re-run the ingest step.
- `reset_password` and `delete_account` are simulated and change nothing outside the app.
- Never commit `.env`. It is git-ignored.
