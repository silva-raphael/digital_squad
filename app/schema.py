from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field

class Role(str, Enum):
    """Enum type class for representing the particpating roles of an inteaction."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

class Message(BaseModel):
    """Class for representing a chat message. 
    
    Can hold system, user, assistant or tool messages.
    """
    # Main attributes
    role: Role = Field(..., description="Role of the entity that sent the message")
    content: str = Field(..., description="Content of the message")

    # Tool specific attributes
    tool_name: Optional[str] = Field(..., description="Name of the called tool")

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