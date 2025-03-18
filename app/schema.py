import inspect
import functools

from typing import Optional, List, Dict, Any, Callable
from enum import Enum

from pydantic import BaseModel, Field

class Tool:
    """Decorator class to convert a function into an LLM-callable tool."""
    def __init__(self, func: Callable):
        """Initialize and store function metadata."""
        self.func = func
    
    def __call__(self) -> Any:
        """Call method that can be used as a callable.
        
        Implemented to allow class to become a decorator.
        """
        return self

    def as_tool(self) -> Dict[str, Any]:
        """Extracts function metadata and returns the formatted dictionary.
        
        Dictionary serves as a LLM description tool
        """
        return {
            "tool_name": self.func.__name__,
            "summary": self.extract_summary(),
            "input": self.extract_arguments_metadata()
        }

    def extract_summary(self) -> str:
        """Extracts the function's docstring summary."""
        return inspect.getdoc(self.func) or "No description provided."

    def extract_arguments_metadata(self) -> Dict[str, str]:
        """Extracts argument names and their descriptions from docstring."""
        signature = inspect.signature(self.func)
        arguments = {}
        docstring = inspect.getdoc(self.func)

        # Extract argument names from the signature
        bound_args = signature.parameters
        for param_name, param in bound_args.items():
            if docstring:
                # Try to find the argument's description in the docstring
                start_index = docstring.find(f"{param_name} (")
                if start_index != -1:
                    end_index = docstring.find(")", start_index)
                    description = docstring[start_index:end_index]
                else:
                    description = "No description available"
                arguments[param_name] = description
            else:
                arguments[param_name] = "No description available"
        return arguments
    
class Role(str, Enum):
    """Enum type class for representing the particpating roles of an inteaction."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

ROLE_TYPE = [role.value for role in Role]

class AgentState(str, Enum):
    """Enum type class for representig the current agent state."""
    IDLE = "idle"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"

class LLMSettings(BaseModel):
    """Wrap all LLM settings.
    
    Implements a wrapper for OpenAI's Chat Completion API
    """
    # Client configuration settings
    model_name: str = Field(..., description="The language model which will generate the completion.")
    api_key: str = Field(..., description="API key")
    base_url: Optional[str] = Field(None, description="Use for OpenAI/Azure OpenAI compatibility")

    # (Optional) Completion configuration settings
    temperature: float = Field(default=0.0, description="Controls randomness: lowering results in less random completions.")
    max_completion_tokens: int = Field(default=4096, description="The maximum number of tokens to generate.")
    top_p: float = Field(default=1, description="Controls diversity via nucleus sampling: 0.5 means half of all likelihood-weighted options are considered.")

class Message(BaseModel):
    """Class for representing a chat message. 
    
    Can hold system, user, assistant or tool messages.
    """
    # Main attributes
    role: Role = Field(..., description="Role of the entity that sent the message")
    content: str = Field(..., description="Content of the message")

    # Tool specific attributes
    tool_name: Optional[str] = Field(None, description="Name of the called tool")

    def to_dict(self) -> dict:
        """Returns the message in dict format"""
        message = {"role": self.role.value}

        if self.content is not None:
            message["content"] = self.content
        if self.tool_name is not None:
            message["tool_name"] = self.tool_name
        
        return message

    @classmethod
    def system_message(cls, content: str) -> "Message":
        """Create a system message"""
        return cls(role=Role.SYSTEM, content=content)
    
    @classmethod
    def user_message(cls, content: str) -> "Message":
        """Create an user message"""
        return cls(role=Role.USER, content=content)
    
    @classmethod
    def assistant_message(cls, content: str) -> "Message":
        """Create an assistant message"""
        return cls(role=Role.ASSISTANT, content=content)
    
    @classmethod
    def tool_message(cls, content: str, tool_name: str) -> "Message":
        """Create a tool message"""
        return cls(role=Role.TOOL, content=content, tool_name=tool_name)

class ScratchPad(BaseModel):
    """Manage agent reasoning process.
    
    Differently from Memory, the scratchpad is used to record the
    agents thinking process, without persisting in memory.
    Only the final action is persisted in order to keep memory clean.
    """
    # Main attributes
    thought: str = Field(None, desciption="Agent's thinking process to drive action")
    action: dict = Field(default_factory=dict, description="Agent's action towards the request")

    # Action's attributes
    tool_name: str = Field(None, description="The name of the selected tool")
    reason: str = Field(None, description="Reason towards choice of the tool")
    tool_input: Dict[str, Any] = Field(default_factory=dict, description="Input parameters for the tool")
    
class Memory(BaseModel):
    """Class for managing agents Memory
    
    Structure for adding, removing, and retrieving messages
    """
    messages: List[Message] = Field(default_factory=list)
    max_messages: int = Field(default=100, description="Max number of messages the memory can hold")

    def add_message(self, message: Message):
        """Adds a single message to memory"""
        self.messages.append(message)

        # Implement limit of messages in memory
        if len(self.messages) > self.max_messages:
            overflow = len(self.messages) - self.messages # compute the amount of messages beyond memory limit
            self.messages = self.messages[overflow:] # always maintain max number of messages in memory removing oldest messages
    
    def clear(self):
        """Delete all messages from memory"""
        self.messages.clear()
    
    def get_recent_messages(self, n: int) -> List[Message]:
        """Return n most recent messages
        
        Args:
            n (int): Number of messages returned
        Returns:
            List[Message]: List of the n most recent Messages
        """
        return self.messages[-n:]
    
    def to_dict_list(self) -> List[dict]:
        """Convert messages to list of dicts"""
        return [msg.to_dict() for msg in self.messages]

if __name__ =="__main__":

    # Testing memory and messages
    memory = Memory()

    user = Message.user_message(content="Hi, I am an user!")
    assistant = Message.assistant_message(content="Hi, I am an assistant!")
    memory.add_message(user)
    memory.add_message(assistant)
    msg_1 = memory.get_recent_messages(1)
    print(msg_1)
    msg_2 = memory.get_recent_messages(10)
    print(msg_2)
    memory.clear()
    msg_3 = memory.get_recent_messages(1)
    print(msg_3)

