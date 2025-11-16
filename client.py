# client.py
import asyncio, sys, os
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main(server_path):
    stack = AsyncExitStack()
    async with stack:
        server_params = StdioServerParameters(command="python", args=[server_path], env=None)
        stdio_transport = await stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        session = await stack.enter_async_context(ClientSession(stdio, write))
        await session.initialize()
        tools = await session.list_tools()
        print("Connected. Tools:", [t.name for t in tools.tools])

        while True:
            q = input("\nQuery (or 'quit'): ").strip()
            if q.lower() in ("quit","exit"):
                break
            # parse simple natural queries
            # example: "predict P1 2025-06-01 14" or "recommend P2 summer 0.25"
            parts = q.split()
            if parts[0].lower()=="predict" and len(parts)>=4:
                product_id = parts[1]
                start_date = parts[2]
                periods = int(parts[3])
                resp = await session.call_tool("predict_demand", {"product_id":product_id, "start_date":start_date, "periods":periods})
                print("Forecast:", resp.content if hasattr(resp,"content") else resp)
            elif parts[0].lower()=="recommend" and len(parts)>=3:
                product_id = parts[1]
                season = parts[2]
                safety = float(parts[3]) if len(parts)>=4 else 0.2
                resp = await session.call_tool("recommend_purchase", {"product_id":product_id, "season":season, "safety_stock_ratio":safety})
                print("Recommendation:", resp.content if hasattr(resp,"content") else resp)
            else:
                print("Commands:\n  predict <P1|P2|...> <YYYY-MM-DD> <periods>\n  recommend <product_id> <season> [safety_ratio]")
        await session.aclose()

if __name__ == "__main__":
    if len(sys.argv)<2:
        print("Usage: python client.py path/to/server.py")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
