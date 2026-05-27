import random


def roll_dice(sides: int = 6, count: int = 1) -> dict:
    """Roll one or more dice.

    Args:
        sides: Number of sides on each die.
        count: Number of dice to roll.

    Returns:
        Individual rolls and their total.
    """
    if sides < 2 or count < 1:
        return {"error": "sides must be at least 2 and count must be at least 1"}

    results = [random.randint(1, sides) for _ in range(count)]
    return {"rolls": results, "total": sum(results)}


dice_tool_definition = {
    "type": "function",
    "function": {
        "name": "roll_dice",
        "description": "Roll one or more dice and return their values and total.",
        "parameters": {
            "type": "object",
            "properties": {
                "sides": {"type": "integer", "description": "Number of sides on each die."},
                "count": {"type": "integer", "description": "Number of dice to roll."},
            },
            "required": ["sides", "count"],
            "additionalProperties": False,
        },
    },
    "strict": True,
}
