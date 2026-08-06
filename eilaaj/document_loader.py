from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from eilaaj import config


def load_documents(data_path: str = config.DATA_PATH):
    """Load every PDF and TXT file in the data directory and return them as documents."""
    pdf_loader = DirectoryLoader(
        data_path,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader,
        show_progress=True,
    )
    txt_loader = DirectoryLoader(
        data_path,
        glob="**/*.txt",
        loader_cls=TextLoader,
        show_progress=True,
    )

    docs = []
    docs.extend(pdf_loader.load())
    docs.extend(txt_loader.load())
    return docs
