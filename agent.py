from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.a2a.utils.agent_to_a2a import to_a2a

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MCP_SERVER = PROJECT_ROOT / "mcp_server" / "mcp_server.py"

db_server_params = StdioServerParameters(
    command="python",
    args=[str(MCP_SERVER)],
)

customer_data_agent = LlmAgent(
    model="gemini-2.5-flash-lite",
    name="customer_data_agent",
    description="Specialist for customer profiles and ticket history via MCP DB tools.",
    instruction=(
        "You are a customer data specialist.\n"
        "- Use MCP tools to read/update customer records.\n"
        "- Use MCP tools to get ticket history for a specific customer.\n"
        "- Never guess IDs; always use IDs given by the router or user.\n"
        "- Clearly show important fields and summarize them.\n"
    ),
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(server_params=db_server_params),
        )
    ],
)

a2a_app = to_a2a(customer_data_agent, port=8001)