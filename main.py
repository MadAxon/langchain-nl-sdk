"""
CLI entry point for Natural Language SDK Agent.

Usage:
    python main.py "создай пользователя с именем Alex"
    python main.py "покажи пользователя Alice"
    python main.py "обнови статус пользователя Bob на active"
    python main.py "выведи всех пользователей"
"""

import sys

# Ensure UTF-8 output encoding across Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from agent import build_agent


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py \"<natural language command>\"")
        print("Examples:")
        print("  python main.py \"создай пользователя с именем Alex\"")
        print("  python main.py \"найди пользователя Alice\"")
        print("  python main.py \"заблокируй пользователя Bob\"")
        print("  python main.py \"покажи список всех пользователей\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    try:
        agent = build_agent()
        result = agent.invoke({
            "messages": [{"role": "user", "content": query}]
        })

        last_message = result["messages"][-1]
        print(last_message.content)
    except Exception as e:
        print("Status: error")
        print(f"Action: Выполнение запроса: '{query}'")
        print("Data: {}")
        print(f"Errors: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
