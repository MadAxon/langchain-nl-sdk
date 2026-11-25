"""
Agent module: initializes Ollama LLM, tools, middleware, system prompt, and agent graph.
"""

import json
import os
import re
from typing import Any, List
from langchain_core.messages import AIMessage, ToolCall
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelResponse

from tools import ALL_TOOLS

DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b-16k")
DEFAULT_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

SYSTEM_PROMPT = """You are a Natural Language SDK Agent for an API service.
Follow these two phases strictly:

Phase 1: Tool Execution.
You MUST call the appropriate tool for every user request. NEVER generate, guess, or hallucinate API data — only use data returned by a tool call. If you do not call a tool, you cannot produce a final answer.

Available tools:
- create_user(name: str, email: str, status: str)
- get_user(user_id: int, name: str)
- update_user_status(new_status: str, user_id: int, name: str)
- list_users(status: str, limit: int)

Phase 2: Final Response Formatting.
Only after you receive the result from the tool may you formulate your final answer strictly in this 4-line format without markdown code blocks:
Status: success | error
Action: <краткое описание действия на русском языке>
Data: <результат данных от инструмента>
Errors: <текст ошибки или 'None'>
"""


def _extract_tool_calls_from_text(content: str) -> List[ToolCall]:
    """Fallback extractor for models returning JSON tool calls in content text."""
    if not content or not content.strip():
        return []

    clean = content.strip()
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", clean, re.DOTALL)
    if not match:
        match = re.search(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", clean, re.DOTALL)
    raw_json = match.group(1) if match else clean

    try:
        data = json.loads(raw_json)
        if isinstance(data, dict) and "name" in data:
            name = data["name"]
            args = data.get("arguments", data.get("args", {}))
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except Exception:
                    args = {}
            if not isinstance(args, dict):
                args = {}
            return [ToolCall(name=name, args=args, id="call_fallback_1")]
    except Exception:
        pass
    return []


@wrap_model_call
def qwen_tool_call_compatibility_middleware(request, handler):
    """
    Middleware ensuring local Qwen2.5-Coder models in Ollama have their tool calls
    parsed correctly even if the model returned JSON in message content.
    """
    response = handler(request)
    updated_result = []
    for msg in response.result:
        if isinstance(msg, AIMessage) and not msg.tool_calls and msg.content:
            calls = _extract_tool_calls_from_text(msg.content)
            if calls:
                msg = AIMessage(
                    content="",
                    tool_calls=calls,
                    response_metadata=msg.response_metadata,
                    id=msg.id
                )
        updated_result.append(msg)
    return ModelResponse(result=updated_result, structured_response=response.structured_response)


def build_agent(model_name: str = DEFAULT_MODEL, base_url: str = DEFAULT_BASE_URL):
    """Constructs and returns the compiled LangChain agent."""
    llm = ChatOllama(
        model=model_name,
        base_url=base_url,
        temperature=0
    )

    agent = create_agent(
        model=llm,
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        middleware=[qwen_tool_call_compatibility_middleware]
    )
    return agent
