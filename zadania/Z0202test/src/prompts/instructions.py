# -*- coding: utf-8 -*-

"""
Centralized repository for instructions, skills, and LLM system prompts.
Define your static prompts here and import them into your MCP server or Agent.
"""

# Example: A general system prompt for your AI Agent
SYSTEM_PROMPT = """
You are an advanced AI assistant powered by Model Context Protocol (MCP).
Your goal is to assist the user by utilizing the available tools efficiently.
Always think step-by-step and provide clear, concise answers.
"""

# Example: An instruction set for a specific skill (e.g., Code Review)
CODE_REVIEW_SKILL = """
When reviewing code, focus on:
1. Security vulnerabilities (e.g., SQL injection, XSS)
2. Performance bottlenecks
3. Code readability and adherence to PEP-8 standards.
Provide actionable feedback.
"""

# Example: A template that requires formatting
def get_summarization_prompt(text: str, max_words: int = 100) -> str:
    return f"""
Please summarize the following text in under {max_words} words.
Highlight the key takeaways.

Text to summarize:
{text}
"""
