from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing_extensions import Self
from typing import Optional

# internal packages
from app.logger import logger
from app.schema import AgentState, Memory, Role, Message
from app.llm import LLM
from app.prompts.default import SYSTEM_INSTRUCTIONS, NEXT_STEP

class BaseAgent(BaseModel):
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

    @model_validator(mode="after")
    def initialize_agent(self) -> Self:
        """Validate agent initialization with default values.
        
        Ensure agent always has Memory, Default Prompts.
        """
        if not self.memory:
            self.memory = Memory()
        
        if not self.system_instructions:
            self.system_instructions = SYSTEM_INSTRUCTIONS
        
        if not self.next_step_instructions:
            self.next_step_instructions = NEXT_STEP

    def update_memory(self, role: Role, content: str) -> None:
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

        if role.value not in message_map:
            raise ValueError(f"Value '{role.value}' does not exist.")
        
        message_method = message_map[role.value]
        message = message_method(content)
        logger.debug(f"Message: {message}")
        logger.debug(f"Type: {type(message)}")
        self.memory.add_message(message)
