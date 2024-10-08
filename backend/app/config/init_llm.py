import os

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate  # type:ignore
from langchain_google_genai import ChatGoogleGenerativeAI

from .logging_config import setup_logging

load_dotenv()
print(f"GOOGLE_API_KEY: {os.getenv('GOOGLE_API_KEY')}")
# Ensure you have set the GOOGLE_API_KEY environment variable
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")


# Initialize logging
logger = setup_logging()


context = ""

template = """
Respond to the following query below.

Here is the conversation history: {context}.

Query: {user_input}
"""
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")


def initialize_llm():
    logger.info("Initializing LLM")
    # global chain  # Declare chain as global to modify it
    try:
        prompt_template = ChatPromptTemplate.from_template(template=template)
        # Create a runnable sequence
        chain = prompt_template | llm
        logger.info(
            "ChatPromptTemplate and LangChain model chain created successfully."
        )
        return chain
    except Exception as e:
        logger.error(f"Failed to create prompt or chain: {e}")


if __name__ == "__main__":
    # Call the method to initialize the LLM
    chain = initialize_llm()
