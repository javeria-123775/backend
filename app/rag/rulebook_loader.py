from langchain_community.document_loaders import PyMuPDFLoader

def load_rulebook(pdf_path: str):

    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()

    return documents