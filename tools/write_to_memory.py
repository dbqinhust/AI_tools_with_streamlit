import json
from datetime import datetime
from pathlib import Path


MEMORY_FILE = Path(__file__).resolve().parents[1] / "data" / "memories.json"


def write_to_memory(memory: str) -> dict:
    """Store important information for future conversations.

    Args:
        memory: Information that should be remembered.

    Returns:
        The status of the write operation.
    """
    try:
        memories = []
        if MEMORY_FILE.exists():
            with MEMORY_FILE.open("r", encoding="utf-8") as file:
                try:
                    memories = json.load(file)
                except json.JSONDecodeError:
                    memories = []

        memories.append(
            {"time": datetime.now().isoformat(timespec="seconds"), "memory": memory}
        )

        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with MEMORY_FILE.open("w", encoding="utf-8") as file:
            json.dump(memories, file, indent=2)

        return {"status": "success", "message": "Memory stored successfully."}
    except OSError as error:
        return {"status": "error", "message": f"Failed to store memory: {error}"}


write_to_memory_tool_definition = {
    "type": "function",
    "function": {
        "name": "write_to_memory",
        "description": "Store information the user specifically asks to remember.",
        "parameters": {
            "type": "object",
            "properties": {
                "memory": {
                    "type": "string",
                    "description": "One to three sentences describing information to remember.",
                }
            },
            "required": ["memory"],
            "additionalProperties": False,
        },
    },
    "strict": True,
}
