from typing import Optional, List
from pydantic import Field

from app.logger import logger
from app.agent.react import ReactAgent
from app.tools.base import Tool
from app.schema import Memory, AgentState, ToolChoice, ToolCall
from app.llm import LLM
from app.prompts.default import SYSTEM_INSTRUCTIONS, NEXT_STEP

class ToolAgent(ReactAgent):
    """ReAct Agent Wrapper, capable of calling and executing tools"""
    # Main attributes:
    name: str
    description: Optional[str] = Field(None, description="Unique description of the agent")

    # Prompts
    system_instructions: str = SYSTEM_INSTRUCTIONS
    next_step_instructions: str = NEXT_STEP

    # Artifacts
    model: LLM = Field(default_factory=LLM)
    memory: Memory = Field(default_factory=Memory)
    state: AgentState = Field(default=AgentState.IDLE)

    # Execution specifications
    max_steps: int = Field(default=2, description="Max execution steps allowed for the agent")
    current_step: int = Field(default=0, description="Current step in execution")

    # Tool specific attributes
    toolbox: List[Tool] = Field(default_factory=list, description="Collection of tools provided to the agent")
    tool_choice: Optional[ToolChoice] = Field(default=ToolChoice.AUTO, description="Definition of how the agent must handle the tools")
    tool_call: Optional[ToolCall] = Field(default_factory=ToolCall, description="Tool response call")

    async def reflect(self) -> bool:
        """Reflects on current state and define next action"""
        # Fetch memory messages
        input_messages = self.messages
        
        try:
            logger.info(f"[{self.name}'s status: {self.state}] {self.name} is currently reflecting...")
            tool_call = await self.model.invoke_tools(input_messages, self.toolbox, self.tool_choice)
        except Exception as e:
            logger.error(f"Error during reflection: {e}")
        
        logger.info(f"[{self.name}'s status: {self.state.value}] {self.name} finished reflecting successfully!")

        # Add response to ToolCall object
        if tool_call:
            self.tool_call.save(tool_call)
            logger.debug(f"ToolCall: {self.tool_call.id}")
            return True
        
        return False

    async def act(self) -> str:
        """Executes an action after reflecting"""
        