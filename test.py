import os
import asyncio
from dotenv import load_dotenv

from app.agent.toolcall import ToolAgent
from app.llm import LLMSettings, LLM
from app.schema import ToolChoice

from app.tools.askuser import ask_user
from app.tools.math import multiply, divide
from app.tools.search import search_duckduckgo

load_dotenv(override=True)

# toggle depending on what model to use
llm_config = LLMSettings(provider="azure",
                         model_name="gpt-4.1-data-ai-br", 
                         api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
                         base_url=os.environ.get("AZURE_OPENAI_ENDPOINT_URL"),
                         api_version=os.environ.get("AZURE_OPENAI_API_VERSION"))

# llm_config = LLMSettings(provider="groq", model_name="llama-3.3-70b-versatile", api_key=os.environ.get("GROQ_API_KEY"))

model = LLM(llm_config)

tools = [multiply, divide, ask_user, search_duckduckgo]

mars = ToolAgent(name="MARS", description="Multi-Agent Reasoning System", model=model, toolbox=tools, tool_choice=ToolChoice.AUTO)

async def main():
    request = """ask my name and birth date and bring me an interesting fdact about it."""
    await mars.run(request)

asyncio.run(main())
