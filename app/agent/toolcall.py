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
    max_steps: int = Field(default=10, description="Max execution steps allowed for the agent")
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
            logger.info(f"[{self.name}'s status: {self.state.value}] {self.name} is currently reflecting...")
            response = await self.model.invoke_tools(input_messages, self.toolbox, self.tool_choice)
        except Exception as e:
            logger.error(f"Error during reflection: {e}")
            raise ValueError(f"Error during reflection: {e}")
        
        logger.info(f"[{self.name}'s status: {self.state.value}] {self.name} finished reflecting successfully!")

        if response and response.tool_calls:
            self.tool_call.save(response.tool_calls)
            '''REMOVE: Just a test'''
            call_parameters = f"tool name called: {self.tool_call.name}, arguments: {self.tool_call.arguments}"
            self.update_memory("assistant", call_parameters)
            '''REMOVE: mAKE THIS MORE BEAUTIFUL'''
            logger.info(f"{self.name} selected tool: {self.tool_call.name}")
        if response and response.content:
            content = response.content
            logger.log("THOUGHT", f"{self.name} thoughts: {content}")

        if self.tool_call.name:
            return True
        
        if content:
            self.update_memory("assistant", content)
            return False

    async def act(self) -> str:
        """Executes an action after reflecting"""
        # Define the map of avaiable tools
        tools_map = {tool.name: tool.func for tool in self.toolbox}

        selected_tool = tools_map[self.tool_call.name]
        try:
            logger.info(f"{self.name} is executing the tool '{self.tool_call.name}' now...")
            result = selected_tool(**self.tool_call.arguments)
        except Exception as e:
            logger.info(f"Failed to execute '{self.tool_call.name}'")
            raise ValueError(f"Failed to execute '{self.tool_call.name}'")
        
        logger.info(f"Tool {self.tool_call.name} was executed successfully!. Tool result: {result}")

        # Updates memory and call llm again with tool result
        self.update_memory("tool", str(result), self.tool_call.id)
        self.tool_call.clear()  # erases previous tool call

        return str(result)

        