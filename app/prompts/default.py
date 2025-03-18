SYSTEM_INSTRUCTIONS = "You are a helpful assistant called NOVA that must help the user"

NEXT_STEP = """Based on the request you should reflect on what you have to do. Output a clear line of thought in the following format:

{
'thought': <your thoughts and reflection>
'action' : {
    'tool_name': <selected_tool>
    'reason': <reason why you chose this specific tool>
    'tool_input': <dictionary following the tool definition>
}
}

Avaiable tools are:

- multiply_two_numbers: {a: float, b: float}

"""