import os
import asyncio
import openai
from agents import Agent,Runner
from agents.mcp import MCPServerSse
from dotenv import load_dotenv
from src.utils.azure_client import azure_openai_model
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_type = os.getenv("AZURE_OPENAI_DEPLOYMENT")
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")

async def main():
    tools_server = MCPServerSse({"url":"http://localhost:8000/mcp"},client_session_timeout_seconds=15.0)
    try:
        await tools_server.connect()
        agent = Agent(
            name="HR Assistant",
            model=azure_openai_model,
            instructions="You are an HR assistant that analyzes resumes. You have a tool to parse resumes for details.",
            mcp_servers=[tools_server]
        )

        task = "List the tools you have and describe them"
        result = await Runner.run(agent,task)
        print("result:", result.final_output)
    finally:
        await tools_server.cleanup()

if __name__ == "__main__":
    asyncio.run(main())


# getting this error https://github.com/tadata-org/fastapi_mcp/issues/134


