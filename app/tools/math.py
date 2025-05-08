from app.tools.base import Tool

@Tool.as_tool
def multiply(a: float, b: float) -> float:
    """Mutiply two numbers
    
    Args:
        a: First number to multiply
        b: Second number to multiply
    
    Returns:
        float: Multiplied result
    """
    return a*b

@Tool.as_tool
def divide(a: float, b: float) -> float:
    """Divide two numbers
    
    Args:
        a: Number 'numerator' to divide
        b: Number 'denominator' to divide by
    
    Returns:
        float: result of division
    """
    return a/b