import re

from app.config import setup_logging

# Initialize logging
logger = setup_logging()


def get_latest_message_cycles(
    conversation_history: str,
    user_name_label: str,
    chatbot_name_label: str,
    num_cycles: int = 5,
) -> str:
    """
    Extracts the latest `num_cycles` message cycles from the conversation history.
    Removes extra newlines inside the AI responses while maintaining a space between user and AI messages.

    Args:
        conversation_history (str): The full conversation history as a string.
        user_name_label (str): Label identifying user messages.
        chatbot_name_label (str): Label identifying bot messages.
        num_cycles (int): The number of latest message cycles to retrieve.

    Returns:
        str: A string containing the latest `num_cycles` message cycles.
    """
    logger.info("Extracting latest message cycles from conversation history.")
    print(f"Full Conversation History:\n{conversation_history}")

    # Regular expressions to identify user_input and ai_response with optional leading whitespace
    user_pattern = re.compile(
        rf"^\s*{user_name_label}\s*(.*)", re.MULTILINE | re.IGNORECASE
    )
    ai_pattern = re.compile(
        rf"^\s*{chatbot_name_label}\s*(.*?)(?=^\s*{user_name_label}|\Z)",
        re.DOTALL | re.MULTILINE | re.IGNORECASE,
    )

    # Find all user inputs
    users = user_pattern.findall(conversation_history)
    logger.info(f"Found {len(users)} user messages.")
    print(f"users: {users}")

    # Find all AI responses
    ais = ai_pattern.findall(conversation_history)
    logger.info(f"Found {len(ais)} bot messages.")
    print(f"ais: {ais}")

    if not users or not ais or len(users) != len(ais):
        logger.warning(
            "Mismatch in number of user and bot messages or no messages found."
        )
        return conversation_history

    # Ensure that each user input has a corresponding AI response
    message_cycles = []
    for user, ai in zip(users, ais):
        # Clean up AI response by stripping leading/trailing whitespace and removing extra newlines inside
        ai_clean = " ".join(
            ai.strip().splitlines()
        )  # Replace newlines with space inside responses
        # Reconstruct the message cycle in the original format
        message_cycle = f"{user_name_label} {user}\n\n{chatbot_name_label} {ai_clean}"
        message_cycles.append(message_cycle)
        logger.debug(f"Processed message cycle: {message_cycle}")

    # Check if the number of message cycles is less than or equal to num_cycles
    if len(message_cycles) <= num_cycles:
        logger.info(
            "Number of message cycles is within the limit. Returning full conversation history."
        )
        return conversation_history

    # Get the latest `num_cycles` message cycles
    latest_cycles = message_cycles[-num_cycles:]
    logger.info(f"Returning the latest {num_cycles} message cycles.")

    # Join them back into a single string with two newlines separating each cycle
    latest_conversation = "\n\n".join(latest_cycles)
    print(f"latest_conversation: {latest_conversation}")
    return latest_conversation
