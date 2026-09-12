MAX_TOOL_RESULT_CHARS = 4_000


def truncate_result(result: str) -> str:
    if len(result) <= MAX_TOOL_RESULT_CHARS:
        return result
    kept = result[:MAX_TOOL_RESULT_CHARS]
    omitted = len(result) - MAX_TOOL_RESULT_CHARS
    return (
        f"{kept}\n\n"
        f"[Truncated. Showed the first {MAX_TOOL_RESULT_CHARS:,} of {len(result):,} "
        f"characters; {omitted:,} omitted. For files, call read_file with offset "
        f"(1-based line) and limit.]"
    )
