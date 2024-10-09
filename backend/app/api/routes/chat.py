from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.constants import (
    CHATBOT_NAME_LABEL,
    CONVERSATIONS_TO_KEEP_IN_CONTEXT,
    USER_NAME_LABEL,
)
from app.core.logging_config import setup_logging
from app.core.utils import initialize_llm, load_chat_history, save_chat_history

# Initialize logging
logger = setup_logging()

router = APIRouter()

chain = initialize_llm()


# Define a request model
class ChatRequest(BaseModel):
    message: str


# Path to store chat history
HISTORY_FILE = "chat_history.json"


@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        print(f"Received message: {request.message}")

        # Load existing chat history
        chat_history = load_chat_history(HISTORY_FILE)

        # Add user input to conversation
        user_input = request.message
        chat_history.append({"role": "user", "content": user_input})

        # Prepare context by keeping the latest N conversation cycles
        context = "\n\n".join(
            [
                f"{USER_NAME_LABEL if msg['role'] == 'user' else CHATBOT_NAME_LABEL} {msg['content']}"
                for msg in chat_history[-CONVERSATIONS_TO_KEEP_IN_CONTEXT * 2 :]
            ]
        )

        logger.info(f"Latest Context for LLM:\n{context}")

        if not context:
            logger.warning(
                "Latest context is empty. The bot will respond without context."
            )

        # Generate a response using the runnable sequence
        try:
            logger.info("Invoking LangChain model with user input and context.")
            response = chain.invoke({"user_input": user_input, "context": context})
            logger.info("Received response from LangChain model.")
            print(f"Bot Response: {response.content}")

            # Add bot response to conversation history
            chat_history.append({"role": "assistant", "content": response.content})

            # Save updated chat history
            save_chat_history(HISTORY_FILE, chat_history)

        except Exception as e:
            logger.error(f"Error invoking LangChain model: {e}")
            response = f"Error: {str(e)}"

        return {"response": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat_history")
async def get_chat_history():
    try:
        chat_history = load_chat_history(HISTORY_FILE)
        return {"history": chat_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
