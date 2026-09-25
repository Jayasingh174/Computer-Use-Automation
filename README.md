# 🤖 Computer Use Automation

An AI-powered browser automation platform that combines **LLM-based planning, Playwright browser control, deterministic replay, safety policies, and human-in-the-loop intervention**.

The system is designed to transform natural-language goals into executable browser actions while maintaining structured artifacts, safety controls, checkpoints, and replayable automation workflows.

---

## 🚀 Overview

**Computer Use Automation** is an experimental AI automation platform built around a simple workflow:

```text
User Goal
   ↓
Groq LLM Planner
   ↓
Structured Action Plan
   ↓
Safety Policy + URL Allowlist
   ↓
Playwright Browser Automation
   ↓
Observation / Execution
   ↓
Checkpoint Verification
   ↓
Result / Human Handoff
```

The project separates **planning** from **execution**, allowing browser workflows to be represented as structured actions and replayed without requiring an LLM for every step.

---

## ✨ Key Features

### 🧠 LLM-Based Computer Use Planning

Uses a Groq-hosted LLM to convert natural-language goals and browser observations into structured actions.

Supported action vocabulary:

```text
navigate
click
fill
select
press
wait
extract
goal_complete
escalate
```

---

### 🌐 Browser Automation

Built with **Playwright** for browser interaction.

The automation layer provides:

* Browser lifecycle management
* Page navigation
* Element interaction
* Form filling
* Keyboard actions
* Text extraction
* Screenshots
* Session management

---

### 🔒 Safety Layer

The execution pipeline includes safety checks before browser actions are performed.

Components include:

```text
ActionPolicy
AllowlistManager
Redaction utilities
```

The allowlist restricts navigation to approved application domains.

---

### 🔁 Deterministic Replay

Previously discovered automation workflows can be represented as `CapabilityArtifact` objects and replayed without asking the LLM to plan every action again.

Replay includes:

* Artifact loading
* Parameter substitution
* Action execution
* Checkpoint verification
* Output extraction
* Error classification

Example:

```text
Capability Artifact
        ↓
ReplayEngine
        ↓
ReplayExecutor
        ↓
ActionExecutor
        ↓
Playwright
        ↓
Checkpoint
        ↓
Outputs
```

---

### 👤 Human-in-the-Loop

The platform supports escalation when an automation task requires human intervention.

The intended flow is:

```text
AI Agent
   ↓
Escalation Required
   ↓
Human Takes Control
   ↓
Human Completes / Reviews Action
   ↓
AI Resumes
```

---

### 📦 Capability Artifacts

Automation workflows are stored as structured artifacts rather than being represented only as raw browser actions.

A capability artifact can contain:

* Artifact ID
* Target URL
* Actions
* Inputs
* Outputs
* Checkpoint
* Metadata
* Status

This provides a foundation for reusable automation capabilities.

---

## 🏗️ Project Architecture

```text
computer-use-automation/
│
├── backend/
│   │
│   ├── app/
│   │   │
│   │   ├── agent/
│   │   │   ├── agent.py
│   │   │   ├── planner.py
│   │   │   ├── observer.py
│   │   │   ├── action_executor.py
│   │   │   └── prompts.py
│   │   │
│   │   ├── api/
│   │   │   ├── dependencies.py
│   │   │   └── routes/
│   │   │       ├── agent.py
│   │   │       ├── artifacts.py
│   │   │       ├── interventions.py
│   │   │       ├── replay.py
│   │   │       └── sessions.py
│   │   │
│   │   ├── artifacts/
│   │   │   ├── schema.py
│   │   │   ├── repository.py
│   │   │   ├── validator.py
│   │   │   └── versioning.py
│   │   │
│   │   ├── automation/
│   │   │   ├── browser.py
│   │   │   ├── session.py
│   │   │   ├── locators.py
│   │   │   └── screenshots.py
│   │   │
│   │   ├── config/
│   │   │   └── settings.py
│   │   │
│   │   ├── escalation/
│   │   │   ├── handoff.py
│   │   │   ├── intervention.py
│   │   │   └── manager.py
│   │   │
│   │   ├── replay/
│   │   │   ├── engine.py
│   │   │   ├── executor.py
│   │   │   ├── checkpoints.py
│   │   │   └── error_handler.py
│   │   │
│   │   ├── safety/
│   │   │   ├── allowlist.py
│   │   │   ├── policy.py
│   │   │   └── redaction.py
│   │   │
│   │   ├── observability/
│   │   │   ├── evidence.py
│   │   │   └── logger.py
│   │   │
│   │   └── utils/
│   │       └── helpers.py
│   │
│   ├── tests/
│   │   ├── test_agent.py
│   │   ├── test_errors.py
│   │   ├── test_handoff.py
│   │   ├── test_observer.py
│   │   ├── test_planner.py
│   │   ├── test_replay.py
│   │   └── test_safety.py
│   │
│   └── requirements.txt
│
├── requirements.txt
└── README.md
```

---

## 🔧 Technology Stack

| Technology            | Purpose                               |
| --------------------- | ------------------------------------- |
| **Python**            | Core backend                          |
| **FastAPI**           | REST API                              |
| **Pydantic**          | Data validation and structured models |
| **Pydantic Settings** | Environment configuration             |
| **Groq**              | LLM-based planning                    |
| **Playwright**        | Browser automation                    |
| **Uvicorn**           | ASGI server                           |
| **Pytest**            | Testing                               |
| **pytest-asyncio**    | Async test support                    |

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/Jayasingh174/computer-use-automation.git
cd computer-use-automation
```

---

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

Install Playwright browsers:

```bash
playwright install chromium
```

---

## 🔐 Environment Configuration

Create a `.env` file inside the `backend` directory.

```env
GROQ_API_KEY=your_groq_api_key

GROQ_BASE_URL=https://api.groq.com/openai/v1

GROQ_MODEL=openai/gpt-oss-120b

DEMO_APP_URL=http://localhost:5173

BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000

MAX_AGENT_STEPS=20
AGENT_TIMEOUT_SECONDS=120

ARTIFACTS_DIR=artifacts
EVIDENCE_DIR=evidence
```

**Never commit your `.env` file or API keys to GitHub.**

---

## ▶️ Running the Backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 🧪 Running Tests

From the `backend` directory:

```bash
pytest
```

For more detailed output:

```bash
pytest -v
```

Async tests can be configured using:

```ini
[pytest]
asyncio_mode = auto
```

---

## 🔄 Agent Execution Flow

The main agent follows an observe → plan → execute loop.

```text
             ┌──────────────┐
             │  User Goal   │
             └──────┬───────┘
                    ↓
             ┌──────────────┐
             │ PageObserver │
             └──────┬───────┘
                    ↓
             ┌──────────────┐
             │ LLM Planner  │
             └──────┬───────┘
                    ↓
             ┌──────────────┐
             │ PlannerAction│
             └──────┬───────┘
                    ↓
          ┌─────────┴─────────┐
          ↓                   ↓
     Goal Complete        Executable
                              Action
                              ↓
                       ┌──────────────┐
                       │ Safety Layer │
                       └──────┬───────┘
                              ↓
                       ┌──────────────┐
                       │ActionExecutor│
                       └──────┬───────┘
                              ↓
                       ┌──────────────┐
                       │  Playwright  │
                       └──────┬───────┘
                              ↓
                         New Observation
```

---

## 🔁 Replay Architecture

Replay allows an existing capability artifact to be executed deterministically.

```text
CapabilityArtifact
       │
       ▼
 ReplayEngine
       │
       ▼
 ReplayExecutor
       │
       ▼
 ActionExecutor
       │
       ▼
 AutomationSession
       │
       ▼
   Playwright
       │
       ▼
CheckpointVerifier
       │
       ▼
    Outputs
```

Parameter placeholders can be resolved during replay:

```text
{{username}}
{{password}}
{{room_number}}
```

Example:

```python
inputs = {
    "username": "demo_user",
    "room_number": "101"
}
```

---

## 🛡️ Canonical Action Format

The project uses a unified action representation:

```python
{
    "type": "click",
    "locator": {
        "value": "#login-button"
    },
    "value": None
}
```

Other examples:

### Navigate

```python
{
    "type": "navigate",
    "value": "http://localhost:5173"
}
```

### Fill

```python
{
    "type": "fill",
    "locator": {
        "value": "#username"
    },
    "value": "demo_user"
}
```

### Press

```python
{
    "type": "press",
    "locator": {
        "value": "#search"
    },
    "value": "Enter"
}
```

### Extract

```python
{
    "type": "extract",
    "locator": {
        "value": ".result"
    }
}
```

---

## 📋 Current Development Status

This repository is an **active development project**.

The architecture currently contains the major components required for an AI browser automation system:

* [x] FastAPI backend
* [x] Groq-based planner
* [x] Structured planner actions
* [x] Playwright automation session
* [x] Browser observation
* [x] Safety policy
* [x] URL allowlist
* [x] Capability artifact schema
* [x] Artifact repository
* [x] Checkpoint verification
* [x] Replay architecture
* [x] Human handoff architecture
* [ ] Complete end-to-end agent execution
* [ ] Complete deterministic replay flow
* [ ] Full automated test coverage
* [ ] Evidence persistence integration
* [ ] Observability/logging integration
* [ ] Production deployment hardening

---

## 🔍 Known Development Items

The current codebase has several integration issues identified during a static dependency and code audit.

### High-priority items

1. Add the computed `demo_app_domain` setting.
2. Unify planner, agent, and executor action vocabularies.
3. Align `ReplayEngine` and `ReplayExecutor` interfaces.
4. Align `ReplayExecutor` with `ActionExecutor`.
5. Fix artifact validation API usage.
6. Connect the human-intervention agent registry.
7. Fix broken test imports and API expectations.
8. Configure async pytest execution.
9. Remove or integrate unused dependencies and modules.
10. Connect evidence and logging components to the execution flow.

These are **development/integration tasks**, not intended to represent the final architecture.

---

## 🧩 Planned Improvements

### Agent

* Better browser-state observation
* Screenshot/vision-based reasoning
* Improved planner prompts
* Action confidence handling
* Retry and recovery strategies
* Agent execution timeout
* Configurable maximum steps

### Safety

* More granular action risk classification
* Domain and route restrictions
* Sensitive-data redaction
* Human confirmation for risky actions

### Replay

* Stronger checkpoint verification
* Better error recovery
* Replay history
* Versioned artifacts
* Parameter validation

### Observability

* Persistent execution evidence
* Screenshot history
* Structured automation logs
* Failure reports
* Discovery/replay traces

### Testing

* Unit tests for core components
* Mocked LLM tests
* Browser integration tests
* Replay integration tests
* Safety regression tests
* End-to-end automation tests

---

## 📁 Core Modules

### `agent/`

Responsible for AI-driven automation.

```text
planner.py          → LLM planning
observer.py         → Browser observation
action_executor.py  → Action execution
agent.py            → Agent orchestration
prompts.py          → Planner prompts
```

### `automation/`

Responsible for browser and session management.

```text
browser.py
session.py
screenshots.py
locators.py
```

### `artifacts/`

Responsible for persistent automation capabilities.

```text
schema.py
repository.py
validator.py
versioning.py
```

### `replay/`

Responsible for deterministic workflow execution.

```text
engine.py
executor.py
checkpoints.py
error_handler.py
```

### `safety/`

Responsible for execution safety.

```text
allowlist.py
policy.py
redaction.py
```

### `escalation/`

Responsible for human intervention.

```text
handoff.py
intervention.py
manager.py
```

### `observability/`

Provides the foundation for execution evidence and logging.

```text
evidence.py
logger.py
```

---

## 🎯 Project Goal

The long-term goal is to build a reliable **AI Computer-Use Automation platform** where users can describe a task in natural language and the system can:

```text
Understand the goal
      ↓
Observe the application
      ↓
Plan browser actions
      ↓
Validate actions for safety
      ↓
Execute through Playwright
      ↓
Verify the result
      ↓
Save the automation capability
      ↓
Replay it deterministically
```

The architecture is intended to bridge **LLM reasoning** with **reliable, structured browser automation** rather than treating every browser interaction as an unstructured LLM response.

---

## ⚠️ Disclaimer

This project is intended for development, experimentation, and learning purposes.

Browser automation can perform actions on external systems. Always use appropriate authorization, access controls, safety restrictions, and test environments when developing or deploying automation workflows.

---

## 👩‍💻 Author

**Jaya Singh**

AI / GenAI Developer

GitHub: [Jayasingh174](https://github.com/Jayasingh174)

---

## 📄 License

Add an appropriate open-source license before distributing this project publicly.
