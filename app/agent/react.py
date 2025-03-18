import re
import ast

from pydantic import Field, model_validator
from typing_extensions import Self

from app.agent.base import BaseAgent, Memory
from app.schema import ScratchPad
from app.prompts.default import NEXT_STEP, SYSTEM_INSTRUCTIONS
from app.logger import logger

class ReactAgent(BaseAgent):
    """ReAct Agent class implementation.
    
    Implementations of the reflect and act methods
    for enhanced agent abilities.
    """
    next_step_instructions: str = NEXT_STEP
    max_steps: int = 1

    async def reflect(self) -> str:
        """Method for agent to reflect on next step and define the course of action"""
        
        # Add trigger for agent to start reflecting on task
        self.update_memory("user", self.next_step_instructions)
        request = self.messages_dict

        logger.info(f"[STATUS: {self.state.value}] '{self.name}' is currently thinking...")
        model_response = self._format_response(self.model.invoke(request))
        logger.log("THOUGHT", f"[STATUS: {self.state.value}] '{self.name}' thoughts: {model_response.get('thought')}")

        # self.update_memory("assistant", model_response)
        return model_response
        
    def act(self) -> str:
        """Method for agent act"""
    
    def _format_response(self, model_response: str) -> dict:
        """Internal method for formatting the model response into a dict object.
        
        Args:
            model_response (str): Language model raw response
        """
        model_response_str = re.sub(r"```json|```", "", model_response).strip()
        return ast.literal_eval(model_response_str)

    async def step(self) -> str:
        return await self.reflect()