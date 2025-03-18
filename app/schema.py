from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field

class Role(str, Enum):
    """Enum type class for representing the particpating roles of an inteaction."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

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
        message = {"role": self.role}

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

class Memory(BaseModel):
    """Class for managing agents memory
    
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

