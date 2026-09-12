import sys

from utils.loop import MODEL, run_agent
from utils.skills import catalogue_section

BASE_PROMPT = "You are a terse coding assistant. Answer in one sentence."
SYSTEM_PROMPT = "\n\n".join(part for part in [BASE_PROMPT, catalogue_section()] if part)


def main() -> None:
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    if len(sys.argv) > 1:
        messages.append({"role": "user", "content": " ".join(sys.argv[1:])})
        print(run_agent(messages))
        return

    print(f"harness · {MODEL} · ctrl-d to quit\n")

    while True:
        try:
            user_input = input("\033[1m> \033[0m")
        except EOFError:
            print()
            break
        if not user_input.strip():
            continue

        messages.append({"role": "user", "content": user_input})

        print(f"\n{run_agent(messages)}\n")


if __name__ == "__main__":
    main()
