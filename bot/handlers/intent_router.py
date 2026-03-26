"""Intent router for natural language queries using LLM."""

import sys
from typing import List, Dict, Any, Optional

from services.llm_client import LLMClient
from services.tools import TOOL_DEFINITIONS, SYSTEM_PROMPT, ToolExecutor


class IntentRouter:
    """Routes natural language queries to appropriate tools using LLM."""

    def __init__(self, llm_client: LLMClient = None, tool_executor: ToolExecutor = None):
        """Initialize the intent router.

        Args:
            llm_client: LLM client for chat completions.
            tool_executor: Tool executor for running tool calls.
        """
        self.llm_client = llm_client or LLMClient()
        self.tool_executor = tool_executor or ToolExecutor()

    def route(self, user_message: str, debug: bool = True) -> str:
        """Route a user message through the LLM tool-calling loop.

        Args:
            user_message: The user's natural language query.
            debug: Whether to print debug output to stderr.

        Returns:
            The final response text.
        """
        # Check if LLM is available
        if not self.llm_client.base_url or not self.llm_client.api_key:
            return self._fallback_response(user_message)

        messages: List[Dict[str, str]] = [
            {"role": "user", "content": user_message}
        ]

        max_iterations = 5
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            try:
                # Call LLM
                response = self.llm_client.chat(
                    messages=messages,
                    tools=TOOL_DEFINITIONS,
                    system_prompt=SYSTEM_PROMPT,
                )
            except Exception as e:
                if debug:
                    print(f"[llm error] {e}", file=sys.stderr)
                return self._fallback_response(user_message)

            # Extract tool calls
            tool_calls = self.llm_client.extract_tool_calls(response)

            if debug:
                if tool_calls:
                    for tc in tool_calls:
                        print(
                            f"[tool] LLM called: {tc['name']}({tc['arguments']})",
                            file=sys.stderr
                        )
                else:
                    text = self.llm_client.get_response_text(response)
                    if text:
                        print(f"[response] LLM responded with text", file=sys.stderr)

            # If no tool calls, return the text response
            if not tool_calls:
                return self.llm_client.get_response_text(response)

            # Execute tools and collect results
            for tc in tool_calls:
                result = self.tool_executor.execute(tc["name"], tc["arguments"])

                if debug:
                    result_str = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
                    print(f"[tool] Result: {result_str}", file=sys.stderr)

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": self._format_tool_result(tc["name"], result),
                })

            if debug:
                print(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM", file=sys.stderr)

        # If we reach max iterations, return a summary
        return "I'm having trouble processing this request. Please try rephrasing your question."

    def _fallback_response(self, message: str) -> str:
        """Return a fallback response when LLM is unavailable.

        Args:
            message: User's message.

        Returns:
            Fallback response with available commands.
        """
        message_lower = message.lower().strip()

        # Simple keyword-based fallback
        if "lab" in message_lower and ("list" in message_lower or "available" in message_lower or "what" in message_lower):
            return "I can list available labs. Use the command: /labs"
        elif "score" in message_lower or "pass" in message_lower:
            return "I can show scores and pass rates. Use: /scores <lab-name>, e.g., /scores lab-04"
        elif "health" in message_lower or "status" in message_lower:
            return "I can check backend health. Use: /health"
        elif "hello" in message_lower or "hi" in message_lower:
            return "Hello! I'm your LMS assistant. I can help you with:\n• /labs - List available labs\n• /scores <lab> - Show pass rates\n• /health - Check backend status\n• /help - All commands"
        elif "help" in message_lower:
            return "Available commands:\n/start - Welcome message\n/help - Show this help\n/health - Check backend status\n/labs - List available labs\n/scores <lab> - Show pass rates for a lab"
        else:
            return "I'm not sure I understand. Here's what I can help with:\n• /labs - List available labs\n• /scores <lab> - Show pass rates\n• /health - Check backend status\n• /help - All commands"

    def _format_tool_result(self, name: str, result: Any) -> str:
        """Format a tool result for the LLM.

        Args:
            name: Tool name.
            result: Tool execution result.

        Returns:
            Formatted result string.
        """
        if isinstance(result, list):
            if not result:
                return "No results found."
            return f"{len(result)} items: {result[:5]}"  # Truncate for context
        elif isinstance(result, dict):
            return str(result)
        else:
            return str(result)


def handle_natural_language(message: str) -> str:
    """Handle a natural language query.

    Args:
        message: User's natural language query.

    Returns:
        Response text.
    """
    router = IntentRouter()
    return router.route(message)
