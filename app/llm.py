from app.schema import LLMSettings

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
    
