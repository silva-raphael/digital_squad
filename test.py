import os
import asyncio
from dotenv import load_dotenv
import pprint

from app.agent.base import BaseAgent
from app.agent.react import ReactAgent
from app.agent.toolcall import ToolAgent
from app.tools.base import Tool
from app.llm import LLMSettings, LLM
from app.logger import logger
from app.schema import Message, ToolChoice

from app.tools.wikipedia import get_wikipedia_summary

load_dotenv(override=True)

llm_config = LLMSettings(model_name="qwen-qwq-32b", api_key=os.environ.get("GROQ_API_KEY"))
model = LLM(llm_config)

@Tool.as_tool
def multiply(a: float, b: float) -> float:
    """Mutiply two numbers
    
    Args:
        a: First number to multiply
        b: Second number to multiply
    
    Returns:
        float: Multiplied result
    """
    return a*b

tools = [multiply, get_wikipedia_summary]

mars = ToolAgent(name="MARS", description="Multi-Agent Reasoning System", model=model, toolbox=tools, tool_choice=ToolChoice.AUTO)

async def main():
    request = "How many Cleopatras existed? Multiply the number by 2"
    await mars.run(request)

asyncio.run(main())
