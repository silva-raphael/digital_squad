from typing import Callable, Dict, Any, Optional
import functools

from app.schema import BaseTool

class Tool:
    """
    Class-based decorator to convert Python functions into OpenAI function format for the Responses API.
    """
    def __init__(self, name: Optional[str] = None, description: Optional[str] = None, strict: bool = True):
        self.name = name
        self.description = description
        self.strict = strict

    def __call__(self, func: Callable):
        func_name = self.name or func.__name__
        docstring = self.description or (func.__doc__.strip() if func.__doc__ else "")

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Extract function parameters
        parameters = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }

        annotations = func.__annotations__
        for param, param_type in annotations.items():
            if param == 'return':
                continue
            
            param_info = {"type": "string"}  # Default to string if not further specified
            if hasattr(param_type, "__origin__") and param_type.__origin__ is list:
                param_info = {"type": "array", "items": {"type": "string"}}
            elif hasattr(param_type, "__origin__") and param_type.__origin__ is dict:
                param_info = {"type": "object"}
            elif isinstance(param_type, type) and param_type.__name__ in ["int", "float", "bool"]:
                param_info = {"type": param_type.__name__}
            
            parameters["properties"][param] = param_info
            parameters["required"].append(param)
        
        wrapper.tool_metadata = BaseTool(
            name=func_name,
            description=docstring,
            parameters=parameters,
            strict=self.strict
        ).model_dump()
        
        return wrapper