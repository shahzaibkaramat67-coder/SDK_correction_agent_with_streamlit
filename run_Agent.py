import json

from Tools import research, search
from model import modelfunction


def run_agent(memory, client, model_name, emit=None, max_steps=25):
    if emit is None:
        emit = lambda event_type, message: print(f"[{event_type}] {message}")

    for _ in range(max_steps):
        response = modelfunction(memory, client, model_name)
        assistant_message = response.choices[0].message
        tool_calls = assistant_message.tool_calls
        if not tool_calls:
            return assistant_message.content

        memory.add_assistant_tool_calls(assistant_message)
        for tool_call in tool_calls:
            name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            query = arguments["query"]
            memory.used_tool(name)

            if name == "search":
                result = search(query=query, emit=emit)
                result = json.dumps({"Tool_name": name, "Tool_Result": result})
            elif name == "research":
                result = research(
                    query=query,
                    sources=memory.get_memory(),
                    emit=emit,
                )
            else:
                raise ValueError(f"Unsupported tool requested by the model: {name}")

            memory.tool_memory("tool", tool_call.id, result)

    raise RuntimeError(f"The agent exceeded its {max_steps}-step limit.")
