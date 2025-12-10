# Assignment 5 – Multi-Agent Customer Service System (MCP + A2A)

This repository implements a **multi-agent customer service system** for the Applied GenAI assignment.

The system uses:

- **Three LLM-backed agents** (Router, Customer Data Agent, Support Agent)
- **Agent-to-Agent (A2A) communication** for coordination
- An **MCP server + SQLite** for customer & ticket data
- An **end-to-end demo** (either `demo.py` or a Colab notebook) that runs the required test scenarios and prints the coordination trace.

---

## 1. Architecture

### 1.1 Agents (A2A layer)

All three agents are **LLM-backed `LlmAgent`s** created with Google ADK and exposed as A2A agents via `to_a2a(...)` + `uvicorn`.

- **Router Agent** – `router_agent/agent.py`
  - Entry point for all user queries.
  - Parses intent (simple lookup, account upgrade, billing/refund, reporting across many customers, multi-intent, etc.).
  - Decides which specialist agent(s) to call via A2A:
    - `customer_data_remote` (Customer Data Agent)
    - `support_remote` (Support Agent)
  - Produces a **coordination log** (bullet points) and then a final natural-language answer.

- **Customer Data Agent** – `customer_data_agent/agent.py`
  - LLM agent specialized in **customer profiles** and **ticket history**.
  - Uses a **MCP toolset** (`McpToolset`) wired to the MCP DB server.
  - Exposes the following MCP-backed tools:
    - `get_customer(customer_id)`
    - `list_customers(status, limit)`
    - `update_customer(customer_id, data)`
    - `create_ticket(customer_id, issue, priority)`
    - `get_customer_history(customer_id)`
    - `list_active_customers_with_open_tickets()` (custom helper for reporting)
  - Typical responsibilities:
    - Look up a single customer by ID.
    - List customers by status (e.g., active).
    - Update customer fields (name, email, phone, status).
    - Create tickets and fetch ticket history.
    - Answer reporting-style questions such as “active customers with open tickets”.

- **Support Agent** – `support_agent/agent.py`
  - LLM agent specialized in **support flows + billing**.
  - Also uses the same MCP toolset (same DB server) for:
    - Creating tickets for urgent issues.
    - Checking customers and their ticket history when needed.
  - Responsibilities:
    - Handle account upgrade and subscription questions.
    - Treat double-charge / refund issues as **high priority** (create a ticket, summarize next steps).
    - Provide customer-friendly explanations and resolutions.

Each agent exposes an A2A endpoint via `to_a2a(..., port=800X)` and is served with `uvicorn` (FastAPI/Starlette under the hood).

---

### 1.2 MCP Server + Database Layer

The MCP layer is implemented in the `mcp_server` package:

- **`mcp_server/db.py`**
  - Wraps access to the SQLite database (`support.db`).
  - Ensures DB initialization via `DatabaseSetup` (`database_setup.py`):
    - Creates tables, triggers.
    - Inserts sample seed data.
  - Helper functions:
    - `ensure_db_initialized()`
    - `fetch_customer(customer_id)`
    - `fetch_customers(status, limit)`
    - `update_customer_record(customer_id, data)`
    - `create_ticket_record(customer_id, issue, priority)`
    - `fetch_ticket_history(customer_id)`
    - `fetch_active_customers_with_open_tickets()`
  - All DB operations use `sqlite3` with `foreign_keys=ON`.

- **`mcp_server/mcp_server.py`**
  - Implements an MCP server over **stdio** using `mcp.server.Server`.
  - Exposes the DB helper functions as MCP tools:

    - `get_customer`
    - `list_customers`
    - `update_customer`
    - `create_ticket`
    - `get_customer_history`
    - `list_active_customers_with_open_tickets`

  - `list_tools` returns the full tool list and JSON Schemas.
  - `call_tool` dispatches to the corresponding handler and returns JSON in a `TextContent` payload.

- **How Agents Talk to MCP**
  - In `customer_data_agent/agent.py` and `support_agent/agent.py`, we use:

    ```python
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    MCP_SERVER = PROJECT_ROOT / "mcp_server" / "mcp_server.py"

    db_server_params = StdioServerParameters(
        command="python",
        args=[str(MCP_SERVER)],
    )

    tools = [
        McpToolset(
            connection_params=StdioConnectionParams(server_params=db_server_params),
        )
    ]
    ```

  - This means **you do not manually run the MCP server**; it is spawned on demand by the agents via stdio.

---

## 2. Repository Structure

```text
Applied_GenAI/
├─ router_agent/
│  └─ agent.py              # Router LLM agent (A2A entry point)
├─ customer_data_agent/
│  └─ agent.py              # Customer Data LLM agent (MCP-backed)
├─ support_agent/
│  └─ agent.py              # Support/Billing LLM agent (MCP-backed)
├─ mcp_server/
│  ├─ db.py                 # SQLite helper layer for customers & tickets
│  └─ mcp_server.py         # MCP server exposing DB tools via stdio
├─ database_setup.py        # Initializes support.db (tables, triggers, seed data)
├─ demo.py                  # Python end-to-end runner
├─ requirements.txt         # Python dependencies (google-adk, mcp, uvicorn, etc.)
└─ README.md                # This file
