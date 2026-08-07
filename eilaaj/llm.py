from langchain_groq import ChatGroq
from eilaaj import config


def get_llm():
    """Return a configured ChatGroq LLM instance."""
    config.check_api_keys()
    return ChatGroq(
        groq_api_key=config.GROQ_API_KEY,
        model_name=config.LLM_MODEL_NAME,
        temperature=config.LLM_TEMPERATURE,
    )
