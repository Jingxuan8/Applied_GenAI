from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from google.adk.runners import InMemoryRunner

from google.adk.a2a.utils.agent_to_a2a import to_a2a

customer_data_remote = RemoteA2aAgent(
    name="customer_data_remote",
    description="Remote client for customer_data_agent (MCP-backed).",
    agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
)

support_remote = RemoteA2aAgent(
    name="support_remote",
    description="Remote client for support_agent (MCP-backed).",
    agent_card=f"http://localhost:8002{AGENT_CARD_WELL_KNOWN_PATH}",
)

router_agent = LlmAgent(
    model="gemini-2.5-flash-lite",
    name="router_agent",
    description="Router/orchestrator for multi-agent customer service with A2A.",
    instruction=(
        "You are the router/orchestrator for a customer support system.\n"
        "Your responsibilities:\n"
        "1. Analyze each user query and detect intents:\n"
        "   - simple lookup (e.g., get info for customer ID N)\n"
        "   - upgrade/account help\n"
        "   - billing/refund issues\n"
        "   - cancellations\n"
        "   - reporting across many customers\n"
        "   - multi-intent (e.g., update email AND show history)\n"
        "2. Decide which remote agent(s) to call and in what order:\n"
        "   - Use customer_data_remote for DB/ticket history operations.\n"
        "   - Use support_remote for upgrades, billing, refunds, cancellations.\n"
        "3. Prefer calling remote agents instead of guessing.\n"
        "4. For each query, ALWAYS output a coordination log first, then the final answer.\n"
        "   Use bullet points, for example:\n"
        "   - [Router] Parsed intents: ...\n"
        "   - [Router -> CustomerData] get_customer(id=12345)\n"
        "   - [CustomerData -> Router] customer is premium\n"
        "   - [Router -> Support] help upgrade premium customer 12345\n"
        "   - [Support -> Router] upgrade flow explained\n"
        "5. For urgent billing issues like 'I've been charged twice' or 'refund immediately',\n"
        "   treat them as high priority and ensure a ticket is created via support_remote.\n"
        "6. For multi-intent queries (e.g., 'Update my email and show my ticket history'),\n"
        "   decompose into sub-tasks and coordinate them.\n"
        "7. For queries like 'Show me all active customers who have open tickets',\n"
        "   delegate to customer_data_remote and let it use the MCP tool that lists\n"
        "   active customers with open tickets, then summarize the results.\n"
    ),
    sub_agents=[customer_data_remote, support_remote],
)

runner = InMemoryRunner(router_agent)

a2a_app = to_a2a(router_agent, port=8003)
