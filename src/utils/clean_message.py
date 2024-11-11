from langchain_core.messages import BaseMessage


def clean_message(message: BaseMessage) -> BaseMessage:
    """Remove fields from messages that are not needed."""
    fields_to_remove = [
        "usage_metadata",
        "invalid_tool_calls",
        "id",
        "example",
        "response_metadata",
    ]
    for field in fields_to_remove:
        if field in message:
            message.pop(field, None)

    return message
