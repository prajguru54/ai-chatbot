from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain_core.runnables import RunnablePassthrough
import os
import logging
import re

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

router = APIRouter()

USER_NAME_LABEL = "===YOU===: "
CHATBOT_NAME_LABEL = "===BOT===: "
CONVERSATIONS_TO_KEEP_IN_CONTEXT = 5


# Ensure you have set the GOOGLE_API_KEY environment variable
os.environ["GOOGLE_API_KEY"] = "AIzaSyApHkOSW2xxZFNwHrfB59cK7tFwjsjuUGs"

# Initialize the Gemini model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

# Create a chat prompt template
template = """
Respond to the following query below.

Here is the conversation history: {context}.

Query: {user_input}
"""

context = ""

try:
    prompt_template = ChatPromptTemplate.from_template(template=template)
    # Create a runnable sequence
    chain = prompt_template | llm
    logger.info("ChatPromptTemplate and LangChain model chain created successfully.")
except Exception as e:
    logger.error(f"Failed to create prompt or chain: {e}")


# Define a request model
class ChatRequest(BaseModel):
    message: str

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
        message_cycle = f"{USER_NAME_LABEL} {user}\n\n{CHATBOT_NAME_LABEL} {ai_clean}"
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



@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    global context
    try:
        print(f"Received message: {request.message}")
        # Add user input to conversation
        user_input = request.message
        
        # Prepare context by keeping the latest N conversation cycles
        latest_context = get_latest_message_cycles(
            conversation_history=context,
            user_name_label=USER_NAME_LABEL,
            chatbot_name_label=CHATBOT_NAME_LABEL,
            num_cycles=CONVERSATIONS_TO_KEEP_IN_CONTEXT,
        )
        logger.info(f"Latest Context for LLM:\n{latest_context}")
        

        if not latest_context:
            logger.warning("Latest context is empty. The bot will respond without context.")
        
        # Generate a response using the runnable sequence
        try:
            logger.info("Invoking LangChain model with user input and context.")
            response = chain.invoke({"user_input": user_input, "context": latest_context})
            logger.info("Received response from LangChain model.")
            print(f"Bot Response: {response.content}")
            # Add user and bot response to conversation
            context += f"{USER_NAME_LABEL} {user_input}\n\n"
            logger.info(f"Updated Conversation with User Input:\n{context}")
            context += f"{CHATBOT_NAME_LABEL} {response.content}\n\n"
            logger.info(f"Updated Conversation with Bot Response:\n{context}")
        except Exception as e:
            logger.error(f"Error invoking LangChain model: {e}")
            response = f"Error: {str(e)}"
        return {"response": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
