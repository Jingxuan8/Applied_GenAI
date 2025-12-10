import asyncio
import json
from typing import Any, Dict

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from db import (
    ensure_db_initialized,
    fetch_customer,
    fetch_customers,
    update_customer_record,
    create_ticket_record,
    fetch_ticket_history,
    fetch_active_customers_with_open_tickets,
)

server = Server("customer-support-db")

# tools/list implementation
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_customer",
            description="Get a single customer by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "Customer ID (customers.id)",
                    }
                },
                "required": ["customer_id"],
            },
        ),
        Tool(
            name="list_customers",
            description="List customers filtered by status with optional limit.",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Customer status: 'active' or 'disabled'",
                        "enum": ["active", "disabled"],
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max rows to return (default 20).",
                        "minimum": 1,
                    },
                },
                "required": ["status"],
            },
        ),
        Tool(
            name="update_customer",
            description=(
                "Update customer fields by ID. "
                "Allowed keys in 'data': name, email, phone, status."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "Customer ID (customers.id)",
                    },
                    "data": {
                        "type": "object",
                        "description": (
                            "Fields to update. Allowed keys: name, email, phone, status."
                        ),
                        "additionalProperties": True,
                    },
                },
                "required": ["customer_id", "data"],
            },
        ),
        Tool(
            name="create_ticket",
            description="Create a new support ticket for a customer.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "Customer ID (tickets.customer_id)",
                    },
                    "issue": {
                        "type": "string",
                        "description": "Ticket issue description.",
                    },
                    "priority": {
                        "type": "string",
                        "description": "Ticket priority.",
                        "enum": ["low", "medium", "high"],
                    },
                },
                "required": ["customer_id", "issue", "priority"],
            },
        ),
        Tool(
            name="get_customer_history",
            description="Get all tickets for a customer (ticket history).",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "Customer ID to fetch ticket history for.",
                    }
                },
                "required": ["customer_id"],
            },
        ),
        Tool(
            name="list_active_customers_with_open_tickets",
            description="List all active customers who have at least one open ticket.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        ),
    ]

# Per-tool handlers
async def handle_get_customer(args: Dict[str, Any]) -> Dict[str, Any]:
    ensure_db_initialized()
    customer_id = int(args["customer_id"])
    customer = fetch_customer(customer_id)
    if customer is None:
        return {
            "ok": False,
            "error": f"Customer with id={customer_id} not found.",
        }
    return {
        "ok": True,
        "customer": customer,
    }


async def handle_list_customers(args: Dict[str, Any]) -> Dict[str, Any]:
    ensure_db_initialized()
    status = args["status"]
    limit = int(args.get("limit", 20))
    customers = fetch_customers(status=status, limit=limit)
    return {
        "ok": True,
        "status": status,
        "count": len(customers),
        "customers": customers,
    }


async def handle_update_customer(args: Dict[str, Any]) -> Dict[str, Any]:
    ensure_db_initialized()
    customer_id = int(args["customer_id"])
    data = dict(args.get("data") or {})

    updated = update_customer_record(customer_id, data)
    if updated is None:
        return {
            "ok": False,
            "error": f"Customer with id={customer_id} not found.",
        }

    return {
        "ok": True,
        "customer": updated,
    }


async def handle_create_ticket(args: Dict[str, Any]) -> Dict[str, Any]:
    ensure_db_initialized()
    customer_id = int(args["customer_id"])
    issue = str(args["issue"])
    priority = str(args["priority"])

    ticket = create_ticket_record(customer_id, issue, priority)
    return {
        "ok": True,
        "ticket": ticket,
    }


async def handle_get_customer_history(args: Dict[str, Any]) -> Dict[str, Any]:
    ensure_db_initialized()
    customer_id = int(args["customer_id"])
    customer = fetch_customer(customer_id)
    if customer is None:
        return {
            "ok": False,
            "error": f"Customer with id={customer_id} not found.",
        }

    tickets = fetch_ticket_history(customer_id)
    return {
        "ok": True,
        "customer": customer,
        "ticket_count": len(tickets),
        "tickets": tickets,
    }

async def handle_list_active_customers_with_open_tickets(
    args: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    ensure_db_initialized()
    customers = fetch_active_customers_with_open_tickets()
    return {
        "ok": True,
        "count": len(customers),
        "customers": customers,
    }

# tools/call implementation
@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    try:
        if name == "get_customer":
            result = await handle_get_customer(arguments)
        elif name == "list_customers":
            result = await handle_list_customers(arguments)
        elif name == "update_customer":
            result = await handle_update_customer(arguments)
        elif name == "create_ticket":
            result = await handle_create_ticket(arguments)
        elif name == "get_customer_history":
            result = await handle_get_customer_history(arguments)
        elif name == "list_active_customers_with_open_tickets":
            result = await handle_list_active_customers_with_open_tickets(arguments)
        else:
            result = {
                "ok": False,
                "error": f"Unknown tool '{name}'.",
            }
    except Exception as e:
        result = {
            "ok": False,
            "error": f"Exception in tool '{name}': {type(e).__name__}: {e}",
        }

    return [
        TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False),
        )
    ]


# stdio entrypoint
async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

if __name__ == "__main__":
    asyncio.run(main())
