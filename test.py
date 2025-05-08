import os
import asyncio
from dotenv import load_dotenv

from app.agent.toolcall import ToolAgent
from app.llm import LLMSettings, LLM
from app.schema import ToolChoice

from app.tools.wikipedia import get_wikipedia_summary
from app.tools.askuser import ask_user
from app.tools.math import multiply, divide
from app.tools.search import search_duckduckgo

load_dotenv(override=True)

llm_config = LLMSettings(model_name="gemma2-9b-it", api_key=os.environ.get("GROQ_API_KEY"))
model = LLM(llm_config)

tools = [multiply, divide, get_wikipedia_summary, ask_user, search_duckduckgo]

mars = ToolAgent(name="MARS", description="Multi-Agent Reasoning System", model=model, toolbox=tools, tool_choice=ToolChoice.AUTO)

async def main():
    request = """I want you to multiply my age by the number of cleopatras that existed. Divide the number by Luan Santana's year of birth."""
    await mars.run(request)

asyncio.run(main())
