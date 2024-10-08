from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import initialize_llm, setup_logging
from app.core.constants import (
    CHATBOT_NAME_LABEL,
    CONVERSATIONS_TO_KEEP_IN_CONTEXT,
    USER_NAME_LABEL,
)
from app.core.utils import get_latest_message_cycles

# Initialize logging
logger = setup_logging()

router = APIRouter()


chain = initialize_llm()


# Define a request model
class ChatRequest(BaseModel):
    message: str


context = ""


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
            logger.warning(
                "Latest context is empty. The bot will respond without context."
            )

        # Generate a response using the runnable sequence
        try:
            logger.info("Invoking LangChain model with user input and context.")
            response = chain.invoke(
                {"user_input": user_input, "context": latest_context}
            )
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
