from langchain_huggingface import HuggingFaceEmbeddings
from eilaaj import config


def get_embeddings_model():
    """Return the HuggingFace embeddings model used across ingestion and retrieval."""
    return HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL_NAME)
