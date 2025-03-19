from abc import abstractmethod

from typing import Optional
from pydantic import Field

from app.agent.base import BaseAgent
from app.schema import AgentState, Memory
from app.llm import LLM
from app.prompts.default import NEXT_STEP, SYSTEM_INSTRUCTIONS

class ReactAgent(BaseAgent):
    """ReAct Agent class implementation.
    
    Implementations of the reflect and act methods
    for enhanced agent abilities.
    """
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

    @abstractmethod
    async def reflect(self) -> bool:
        """Reflects on current state and define next action"""
    
    @abstractmethod
    async def act(self) -> str:
        """Executes an action after reflecting"""

    async def step(self) -> str:
        reflection_result = await self.reflect()
        
        # Checks if any action is needed
        if not reflection_result:
           return "Reflecting completed: no more needed actions"
        
        return await self.act()
