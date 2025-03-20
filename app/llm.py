from typing import List

from app.schema import LLMSettings, Message, ToolChoice
from app.tools.base import Tool

from app.logger import logger

# Groq API,
from groq import AsyncGroq

class LLM:
    """Wrapper class for LLM calls"""
    def __init__(self, llm_config: LLMSettings):
        self.model_name = llm_config.model_name
        self.api_key = llm_config.api_key
        self.base_url = llm_config.base_url
        self.temperature = llm_config.temperature
        self.max_completion_tokens = llm_config.max_completion_tokens
        self.top_p = llm_config.top_p

        # Initialize model
        self.client = AsyncGroq(
            api_key=self.api_key,
            base_url=self.base_url,
            )
    
    def format_messages(self, messages: List[Message]) -> List[dict]:
        """Formats messages to LLM format.
        
        Receives messages and converts to a dict in OpenAI format

        Args:
            messages: A list of messages as Message object

        Returns:
            A list of messages in dictionary format, followig OpenAI's pattern

        Example:
            >>> message = [
            ...             Message.system_message("You are a helpful assistant"),
            ...             Message.user_message("Hi, how are you?"),
            ...             Message.assistant_message("I am fine! How can I help you?")
            ...           ]
            >>> formatted = messages.format_messages(message)
        """
        formatted_messages = []
        for message in messages:
            formatted_messages.append(message.to_dict())
        
        return formatted_messages
    
    async def invoke(self, conversation_messages: List[Message]) -> str:
        """Invokes the Language Model.
        
        Calls the Chat completion API.

        Args:
            conversation_messages: List of conversation messages
            system_message: List of system messages to add before the conversation
        
        Returns:
            Models text response

        Example: 
        >>> response = llm.invoke(Message.user_message("Hi, how are you?"))
        """
        formatted_messages = []

        conversation_messages = self.format_messages(conversation_messages)
        formatted_messages.extend(conversation_messages)

        response = await self.client.chat.completions.create(
            messages=formatted_messages,
            model=self.model_name,
        )

        return response.choices[0].message.content

    async def invoke_tools(self, 
                           conversation_messages: List[Message], 
                           tools: List[Tool],
                           tool_choice: ToolChoice = ToolChoice.AUTO) -> str:
        """Invokes the langugae model with tools.
        
        Allows the use of tools for the call
        """
        formatted_messages = []

        conversation_messages = self.format_messages(conversation_messages)
        formatted_messages.extend(conversation_messages)

        # Unpack all provided tools for use
        toolbox = [t.tool_metadata for t in tools]

        response = await self.client.chat.completions.create(
            messages=formatted_messages,
            model=self.model_name,
            tools=toolbox,
            tool_choice=tool_choice.value,
        )

        return response.choices[0].message