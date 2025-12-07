import asyncio
from router_agent.agent import runner

TEST_QUERIES = [
    "Get customer information for ID 5",
    "I'm customer 12345 and need help upgrading my account",
    "Show me all active customers who have open tickets",
    "I've been charged twice, please refund immediately!",
    "Update my email to new@email.com and show my ticket history",
]


async def main():
    for q in TEST_QUERIES:
        print("=" * 80)
        print(f"USER: {q}\n")

        await runner.run_debug(q, verbose=True)

        print("\n")


if __name__ == "__main__":
    asyncio.run(main())