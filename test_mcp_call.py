import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json

async def main():
    async with AsyncExitStack() as stack:
        server_params = StdioServerParameters(command='python', args=['server.py'])
        stdio_transport = await stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        session = await stack.enter_async_context(ClientSession(stdio, write))
        await session.initialize()
        result = await session.call_tool('predict_demand', {'product_id':'P1','start_date':'2025-11-17','periods':3})
        def safe(obj):
            if obj is None or isinstance(obj, (str,int,float,bool)):
                return obj
            if isinstance(obj, dict):
                return {k: safe(v) for k,v in obj.items()}
            if isinstance(obj, list):
                return [safe(v) for v in obj]
            if hasattr(obj,'content'):
                return safe(getattr(obj,'content'))
            if hasattr(obj,'text'):
                return safe(getattr(obj,'text'))
            try:
                return str(obj)
            except Exception:
                return None
        if hasattr(result,'content'):
            print(json.dumps(safe(result.content)))
        else:
            print(json.dumps({'error':'No content in result'}))

if __name__ == '__main__':
    asyncio.run(main())
