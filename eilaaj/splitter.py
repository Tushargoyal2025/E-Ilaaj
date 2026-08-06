from langchain_text_splitters import RecursiveCharacterTextSplitter
from eilaaj import config


def split_into_chunks(documents):
    """Split documents into chunks using the configured size and overlap."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    return text_splitter.split_documents(documents)
