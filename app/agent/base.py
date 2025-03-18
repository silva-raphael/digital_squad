from contextlib import asynccontextmanager
from abc import abstractmethod, ABC

from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing_extensions import Self
from typing import Optional, List

# internal packages
from app.logger import logger
from app.schema import AgentState, Memory, Role, Message, ROLE_TYPE
from app.llm import LLM
from app.prompts.default import SYSTEM_INSTRUCTIONS, NEXT_STEP

class BaseAgent(ABC, BaseModel):
    """Abstract class for Agents.

    Abstract class that manages the base functionalities of an agent, such as: memory managament,
    state transition and step-by-step execution
    """
    model_config = ConfigDict(arbitrary_types_allowed=True) # allow non pydantic classes 
    
    # Main attributes:
    name: str = Field(..., description="Unique and descriptive name for the agent")
    description: Optional[str] = Field(None, description="Unique description of the agent")

    # Prompts
    system_instructions: str = Field(None, description="Main instructions of the agent")
    next_step_instructions: str = Field(None, description="Prompt for determining the next step")

    # Artifacts
    model: LLM = Field(..., description="LLM object used for completion")
    memory: Memory = Field(None, description="Agent memory")
    state: AgentState = Field(default=AgentState.IDLE, description="Current agent state")

    # Execution specifications
    max_steps: int = Field(default=10, description="Max execution steps allowed for the agent")
    current_step: int = Field(default=0, description="Current step in execution")

    @model_validator(mode="after")
    def initialize_agent(self) -> Self:
        """Validate the agent is correctly initialized.
        
        Ensure agents have memory with loaded system instructions
        """
        if not self.system_instructions:
            self.system_instructions = SYSTEM_INSTRUCTIONS
        if not self.next_step_instructions:
            self.next_step_instructions = NEXT_STEP
        if not self.memory:
            self.memory = Memory()
            self.update_memory("system", self.system_instructions)
        
        return self

    def update_memory(self, role: str, content: str) -> None:
        """Add message to the agent memory

        Args:
            role (Role): Role of message sender (system, assistant, user, tool)
            content (str): Message text content
        """
        message_map = {
            "system": Message.system_message,
            "assistant": Message.assistant_message,
            "user": Message.user_message,
            "tool": Message.tool_message
        }

        if role not in message_map:
            raise ValueError(f"Role '{role}' not allowed. Allowed types are: {', '.join(role for role in ROLE_TYPE)}")
        
        message_method = message_map[role]
        message = message_method(content)

        self.memory.add_message(message)
    
    @asynccontextmanager
    async def state_context(self, new_state: AgentState):
        """A context manager for safe state transitions.
        
        Args:
            new_state (AgentState): Receives the new agent state
        """
        if not isinstance(new_state, AgentState):
            raise ValueError(f"State '{new_state}' not allowed.")
        
        previous_state = self.state
        self.state = new_state

        try:
            yield
        except Exception as e:
            self.state = AgentState.ERROR   # revert to error state if process fails 
            raise e
        finally:
            self.state = previous_state

    @abstractmethod
    async def step(self) -> str:
        """Abstract method controlling the next step of the agent.
        
        Must be implemented with the desired functionality.
        """
        raise NotImplementedError

    async def run(self, request: str) -> str:
        """Run the agent based on a request.
        
        request (str): Text request from user, other agents or tool
        """
        results: list[str] = []

        async with self.state_context(AgentState.RUNNING):
            while self.current_step < self.max_steps and self.state != AgentState.FINISHED:
                self.current_step += 1
                logger.info(f"['{self.name}' STATUS: {self.state.value}] Initiating step {self.current_step}/{self.max_steps} for agent '{self.name}'")
                if request:
                    self.update_memory("user", request) # Add the user request to the agent memory
                
                step_result = await self.step()
                logger.info(f"['{self.name}' STATUS: {self.state.value}] Appending result from step {self.current_step}")
                results.append(step_result)

                # Clean request
                request = None
            
            if self.current_step >= self.max_steps:
                self.state = AgentState.FINISHED
                logger.info(f"['{self.name}' STATUS: {self.state.value}] Agent '{self.name}' process terminated. Max steps reached.")
        
        return results if results else "No steps executed"
    
    @property
    def messages(self) -> List[Message]:
        """Retrieve a list of Messages from agents memory"""
        return self.memory.messages
    
    @property
    def messages_dict(self) -> List[dict]:
        return [msg.to_dict() for msg in self.memory.messages]