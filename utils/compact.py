import json

COMPACT_ABOVE_TOKENS = 60_000  # ~65% of the window
KEEP_LAST = 8


def estimate_tokens(messages) -> int:
    return max(1, len(json.dumps(messages, default=str)) // 4)


# You cannot slice the transcript anywhere.
# A tool message is meaningless without the assistant message whose tool_calls it answers.
def split_at_safe_boundary(messages, keep_last: int) -> int:
    """Index to cut at that never orphans a tool result."""
    cut = max(1, len(messages) - keep_last)
    while cut < len(messages) and messages[cut]["role"] == "tool":
        cut -= 1  # back up onto the assistant that made the call
    return max(cut, 1)


def compact(messages, client, model):
    cut = split_at_safe_boundary(messages, KEEP_LAST)
    system_prompt, older, recent = messages[0], messages[1:cut], messages[cut:]
    if not older:
        return messages

    rendered = "\n".join(
        f"[{m['role']}] {(m.get('content') or '')[:2000]}" for m in older
    )
    summary = (
        client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Summarise this coding session. Preserve: the user's goal, files "
                    "inspected and what they contained, edits already made, and anything "
                    "still outstanding. Drop conversational filler.",
                },
                {"role": "user", "content": rendered},
            ],
        )
        .choices[0]
        .message.content
    )

    return [
        system_prompt,
        {"role": "user", "content": f"[Earlier in this session]\n{summary}"},
    ] + recent
