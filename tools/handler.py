from model_client import ToolSpec

from .read_from_memory import read_from_memory, read_from_memory_tool_definition
from .roll_dice import dice_tool_definition, roll_dice
from .search_help_center import retrieval_tool_definition, search_help_center
from .write_to_memory import write_to_memory, write_to_memory_tool_definition


def _responses_schema(definition: dict) -> dict:
    schema = {"type": "function", **definition["function"]}
    if "strict" in definition:
        schema["strict"] = definition["strict"]
    return schema


TOOL_SPECS = {
    "roll_dice": ToolSpec(roll_dice, _responses_schema(dice_tool_definition)),
    "search_help_center": ToolSpec(
        search_help_center, _responses_schema(retrieval_tool_definition)
    ),
    "read_from_memory": ToolSpec(
        read_from_memory, _responses_schema(read_from_memory_tool_definition)
    ),
    "write_to_memory": ToolSpec(
        write_to_memory, _responses_schema(write_to_memory_tool_definition)
    ),
}


def get_tool_specs(*names: str) -> list[ToolSpec]:
    return [TOOL_SPECS[name] for name in names]
