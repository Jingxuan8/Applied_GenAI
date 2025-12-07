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

support_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="support_agent",
    description="Handles general support, billing, cancellations, and escalation.",
    instruction=(
        "You are a customer support specialist.\n"
        "- Handle questions about accounts, upgrades, and subscriptions.\n"
        "- For billing issues (double charges, refunds), treat them as high priority.\n"
        "- When appropriate, create a support ticket via MCP tools.\n"
        "- Summarize the customer's issue, the action you took, and next steps.\n"
    ),
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(server_params=db_server_params),
        )
    ],
)

a2a_app = to_a2a(support_agent, port=8002)
