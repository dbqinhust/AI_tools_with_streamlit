import json
from pathlib import Path


FAQ_FILE = Path(__file__).resolve().parents[1] / "data" / "help_center_faq.json"


def search_help_center(query: str) -> str:
    """Search the help center FAQ for a support topic.

    Args:
        query: A support topic such as refund policy or shipping time.

    Returns:
        The matching FAQ answer or a support fallback message.
    """
    with FAQ_FILE.open("r", encoding="utf-8") as file:
        faq_data = json.load(file)

    normalized_query = query.strip().lower()
    if normalized_query in faq_data:
        return faq_data[normalized_query]
    return (
        f"Sorry, I don't have information about '{query}' in our help center yet. "
        "Please contact support for assistance."
    )


retrieval_tool_definition = {
    "type": "function",
    "function": {
        "name": "search_help_center",
        "description": (
            "Search the company help center FAQs for refund policy, shipping time, "
            "reset password, cancel subscription, track order, contact support, "
            "product warranty, or size guide."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A help center FAQ topic.",
                    "enum": [
                        "refund policy",
                        "shipping time",
                        "reset password",
                        "cancel subscription",
                        "track order",
                        "contact support",
                        "product warranty",
                        "size guide",
                    ],
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    "strict": True,
}
