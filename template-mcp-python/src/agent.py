from src.helpers.logger import log

class Agent:
    def __init__(self, name: str = "TemplateAgent"):
        self.name = name

    async def run(self, task: str):
        """
        Main execution loop for the agent.
        Integrate LLM calls and tool execution here.
        """
        log.info(f"[{self.name}] Starting task: {task}")
        # TODO: Implement agentic loop (e.g., Anthropic API / OpenAI API calling MCP tools)
        pass
