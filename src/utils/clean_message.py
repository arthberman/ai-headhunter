from langchain_core.messages import BaseMessage


def clean_message(message: BaseMessage) -> BaseMessage:
    """Remove fields from messages that are not needed."""
    # Copy the message to avoid modifying the original
    updated_message = message.model_copy()
    fields_to_remove = [
        "usage_metadata",
        "invalid_tool_calls",
        "id",
        "example",
        "response_metadata",
    ]
    print("clean_message")
    # Remove fields from additional_kwargs if they exist
    if hasattr(updated_message, "additional_kwargs"):
        for field in fields_to_remove:
            updated_message.additional_kwargs.pop(field, None)

    # Remove direct attributes if they exist
    for field in fields_to_remove:
        if hasattr(updated_message, field):
            delattr(updated_message, field)

    return updated_message
