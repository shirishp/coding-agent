import sys

from utils.loop import MODEL, run_agent
from utils.prompt import build_system_prompt


def main() -> None:
    messages = [
        {
            "role": "system",
            "content": build_system_prompt(),
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
