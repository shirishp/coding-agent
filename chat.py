import sys

from coding_agent.loop import run_agent
from coding_agent.prompt import build_system_prompt
from coding_agent.runtime import Runtime


def main() -> None:
    runtime = Runtime.from_env()
    messages = [
        {
            "role": "system",
            "content": build_system_prompt(runtime),
        }
    ]

    if len(sys.argv) > 1:
        messages.append({"role": "user", "content": " ".join(sys.argv[1:])})
        print(run_agent(messages, runtime))
        return

    print(f"harness · {runtime.model} · ctrl-d to quit\n")

    while True:
        try:
            user_input = input("\033[1m> \033[0m")
        except EOFError:
            print()
            break
        if not user_input.strip():
            continue

        messages.append({"role": "user", "content": user_input})

        print(f"\n{run_agent(messages, runtime)}\n")


if __name__ == "__main__":
    main()
