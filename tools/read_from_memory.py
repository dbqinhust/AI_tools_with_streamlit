import json
from pathlib import Path


MEMORY_FILE = Path(__file__).resolve().parents[1] / "data" / "memories.json"


def read_from_memory() -> dict:
    """Read all remembered information.

    Returns:
        Stored memories with timestamps, or a status message if none exist.
    """
    try:
        if not MEMORY_FILE.exists():
            return {"status": "success", "memories": "No memories stored yet."}

        with MEMORY_FILE.open("r", encoding="utf-8") as file:
            try:
                memories = json.load(file)
            except json.JSONDecodeError:
                memories = []

        if not memories:
            return {"status": "success", "memories": "No memories stored yet."}

        memory_strings = [
            f"{entry['time']}: {entry['memory']}" for entry in memories
        ]
        return {"status": "success", "memories": "\n".join(memory_strings)}
    except (OSError, json.JSONDecodeError, KeyError) as error:
        return {"status": "error", "message": f"Failed to retrieve memories: {error}"}


read_from_memory_tool_definition = {
    "type": "function",
    "function": {
        "name": "read_from_memory",
        "description": "Retrieve all stored memories with their timestamps.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    "strict": True,
}
