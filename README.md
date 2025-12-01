# Assignment 5 – Multi-Agent Customer Service System (MCP + A2A)

This repository implements a multi-agent customer service system using:

- An **MCP server** for database tools (`tools/list` and `tools/call`)
- **A2A-compatible agents** (Router Agent, Customer Data Agent, Support Agent)
- An end-to-end **Python demo** that runs all required scenarios (5 test cases + 3 story scenarios)

---

## 1. Files

- `assignment5.py`  
  - **MCP server implementation**
    - `run_mcp_stdio()`
    - `@server.list_tools`
    - `@server.call_tool`
  - **MCP tools**
    - `get_customer(customer_id)`
    - `list_customers(status, limit)`
    - `update_customer(customer_id, data)`
    - `create_ticket(customer_id, issue, priority)`
    - `get_customer_history(customer_id)`
  - **Core agents (Python-level)**
    - `router_agent(user_query: str)`
    - `customer_data_agent(task: dict)`
    - `support_agent(task: dict)`
  - **A2A agent wrappers** (when `python_a2a` is installed)
    - `CustomerDataA2A` – wraps Customer Data Agent
    - `SupportA2A` – wraps Support Agent
    - `RouterA2A` – wraps Router Agent
  - **End-to-end demo runner**
    - `run_assignment_test_scenarios()`  
      Runs:
      - 5 official test scenarios
      - 3 “story” scenarios (task allocation, negotiation, multi-step)

- `database_setup.py`  
  - Instructor-provided script used by `ensure_db_initialized()`.
  - Creates `support.db`, tables, triggers, and inserts sample data the first time the MCP tools are called.

- `requirements.txt`  
  - Python dependencies for MCP + A2A:
    - `mcp`
    - `python-a2a[all]`

- `run_demo.sh`  
  - Convenience script to run all 8 scenarios end-to-end:
    - Calls: `python assignment5.py demo`
  - Shows full logs of:
    - Router → DataAgent
    - Router → SupportAgent
    - Final user-facing answers

- `run_mcp.sh`  
  - Convenience script to start the MCP stdio server:
    - Calls: `python assignment5.py mcp`
  - Can be used with an external MCP client (e.g. MCP Inspector) to exercise `tools/list` and `tools/call`.

---

## 2. Environment Setup (local)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
