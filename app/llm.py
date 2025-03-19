from typing import List

from app.schema import LLMSettings, Message

# Groq API,
from groq import Groq

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
        self.client = Groq(
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
    
    def invoke(self, conversation_messages: List[Message], system_messages: List[Message] = None) -> str:
        """Invokes the Language Model.
        
        Calls the Chat completion API.

        Args:
            conversation_messages: List of conversation messages
            system_message: List of system messages to add before the conversation
        
        Returns:
            Models text response
        Example: 
        >>> messages = {"role": Role.ASSISTANT, "content": "Hi, how can I help you?"}
        """
        formatted_messages = []

        # Check if any system messages were sent to append before the conversation messages
        if system_messages:
            formatted_sys_msg = self.format_messages(system_messages)
            formatted_messages.append(formatted_sys_msg)

        conversation_messages = self.format_messages(conversation_messages)
        formatted_messages.append(conversation_messages)

        chat_completion = self.client.chat.completions.create(
            messages=formatted_messages,
            model=self.model_name
        )

        return chat_completion.choices[0].message.content
    

    
