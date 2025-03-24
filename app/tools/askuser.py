from app.tools.base import Tool

@Tool.as_tool
def ask_user(question: str) -> str:
    """Ask the user a question
    
    Args:
        question: Question to the user to answer
    
        Returns:
            User response
    """
    
    answer = input(f"{question}\n")
    return answer