from typing import Callable, Optional, Dict, Any
import functools

class Tool:
    """
    Converts Python functions into OpenAI function-callable format.
    """
    def __init__(self, func: Callable, name: Optional[str] = None, description: Optional[str] = None, strict: bool = True):
        self.func = func
        self.name = name or func.__name__
        self.description = description or (func.__doc__.strip() if func.__doc__ else "")
        self.strict = strict
        self.tool_metadata = self._extract_metadata()

        # Preserve function attributes
        functools.update_wrapper(self, func)

    def _extract_metadata(self) -> Dict[str, Any]:
        """Extract function metadata to match OpenAI's function-calling format."""
        parameters = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }

        annotations = self.func.__annotations__
        for param, param_type in annotations.items():
            if param == 'return':
                continue

            param_info = {"type": "string"}  # Default to string
            if hasattr(param_type, "__origin__") and param_type.__origin__ is list:
                param_info = {"type": "array", "items": {"type": "string"}}
            elif hasattr(param_type, "__origin__") and param_type.__origin__ is dict:
                param_info = {"type": "object"}
            elif isinstance(param_type, type) and param_type.__name__ in ["int", "float", "bool"]:
                param_info = {"type": param_type.__name__}

            parameters["properties"][param] = param_info
            parameters["required"].append(param)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": parameters,
                "strict": self.strict
            }
        }
    
    def __call__(self, *args, **kwargs):
        """Execute the wrapped function."""
        return self.func(*args, **kwargs)

    @staticmethod
    def as_tool(func: Callable = None, *, name: Optional[str] = None, description: Optional[str] = None, strict: bool = True) -> "Tool":
        """
        Converts a function into a Tool instance.
        Can be used as:
        
        - `@as_tool`
        - `as_tool(func)`
        """
        if func is None:
            return lambda f: Tool.as_tool(f, name=name, description=description, strict=strict)

        if not callable(func):
            raise TypeError(f"Expected a function, but got {type(func)}")

        return Tool(func, name, description, strict)