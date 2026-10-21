class Memory:
    def __init__(self):
        self.messages = []
        self.tool_used = []

    def add_memory(self, role, content):
        self.messages.append({"role": role, "content": content})

    def tool_memory(self, role, tool_call_id, content):
        self.messages.append(
            {"role": role, "tool_call_id": tool_call_id, "content": content}
        )

    def add_assistant_tool_calls(self, message):
        self.messages.append(message.model_dump(exclude_none=True))

    def used_tool(self, name):
        self.tool_used.append({"name": name})

    def get_memory(self):
        return self.messages[:]

    def get_text(self):
        return "\n".join(f"{m['role']} - {m['content']}" for m in self.get_memory())
