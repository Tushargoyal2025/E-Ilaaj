import os
from langchain_chroma import Chroma
from eilaaj import config
from eilaaj.embeddings import get_embeddings_model


def build_vector_store(chunks):
    """Build a fresh Chroma vector store from document chunks and persist it to disk."""
    embeddings_model = get_embeddings_model()
    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings_model,
        persist_directory=config.PERSIST_DIRECTORY,
    )


def load_vector_store(persist_directory: str = config.PERSIST_DIRECTORY):
    """Load an existing Chroma vector store from disk."""
    embeddings_model = get_embeddings_model()
    return Chroma(persist_directory=persist_directory, embedding_function=embeddings_model)


def vector_store_exists(persist_directory: str = config.PERSIST_DIRECTORY) -> bool:
    """Check whether a persisted vector store already exists on disk."""
    return os.path.exists(persist_directory) and len(os.listdir(persist_directory)) > 0


def get_retriever(vector_store, top_k: int = config.TOP_K_RESULTS):
    """Return a retriever for the given vector store."""
    return vector_store.as_retriever(search_kwargs={"k": top_k})
