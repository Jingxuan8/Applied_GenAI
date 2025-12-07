# Assignment 5 – Multi-Agent Customer Service System (MCP + A2A)

This repository implements a **multi-agent customer service system** for the Applied GenAI assignment.

The system uses:

- **Three LLM-backed agents** (Router, Customer Data Agent, Support Agent)
- **Agent-to-Agent (A2A) communication** for coordination
- **MCP server + SQLite** for customer & ticket data
- An **end-to-end demo script** (`demo.py`) that runs the required test scenarios and prints the full trace of agent coordination.

---

## 1. Architecture

### 1.1 Agents

- **Router Agent (`router_agent/agent.py`)**
  - Entry point for all user queries
  - Parses intent (lookup, account upgrade, refund, reporting, multi-intent, etc.)
  - Decides which specialist agent(s) to call via A2A
  - Synthesizes final answer for the user

- **Customer Data Agent (`customer_data_agent/agent.py`)**
  - Specialist for **customer profiles** and **ticket history**
  - Exposes MCP tools on top of a SQLite database:
    - `get_customer(customer_id)`
    - `list_customers(status, limit)`
    - `update_customer(customer_id, data)`
    - `create_ticket(customer_id, issue, priority)`
    - `get_customer_history(customer_id)`

- **Support Agent (`support_agent/agent.py`)**
  - Specialist for **support flows**, especially **billing and refunds**
  - Handles:
    - Account upgrade questions
    - Double-charge / refund issues (treated as *high priority*)
    - Ticket creation using MCP tools
  - Coordinates with customer data when necessary

### 1.2 Database (MCP)

- SQLite database: `support.db`
- Initialized via `database_setup.py` (tables, triggers, sample data)
- Tables:
  - `customers`
  - `tickets`
- Each MCP tool in the agents maps directly to SQL operations on this DB.

---

## 2. Repository Structure

```text
Applied_GenAI/
├─ router_agent/
│  └─ agent.py              # Router agent (LLM + A2A)
├─ customer_data_agent/
│  └─ agent.py              # Customer Data Agent + MCP tools
├─ support_agent/
│  └─ agent.py              # Support Agent + MCP tools
├─ database_setup.py        # Creates support.db, tables, triggers, seed data
├─ demo.py                  # End-to-end demo runner (A2A + MCP)
├─ requirements.txt         # (Optional) Python dependencies
└─ README.md                # This file
