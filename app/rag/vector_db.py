import os
import shutil
from typing import List, Union

from langchain_chroma import Chroma
from langchain_core.documents import Document



# -------------------------------------------------------
# CREATE NEW CHROMA VECTORSTORE
# -------------------------------------------------------
def create_vector_db(
    embeddings,
    persist_dir: str,
    collection_name: str = "pra_lcr_collection",
    fresh: bool = True
) -> Chroma:

    # Clean persistence directory
    if fresh and os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)

    os.makedirs(persist_dir, exist_ok=True)
    os.chmod(persist_dir, 0o777)

    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )

    return vectorstore


# -------------------------------------------------------
# LOAD EXISTING VECTORSTORE
# -------------------------------------------------------
def load_vector_db(
    embeddings,
    persist_dir: str,
    collection_name: str = "pra_lcr_collection"
) -> Chroma:

    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )


# -------------------------------------------------------
# CLEAN DOCUMENT METADATA
# -------------------------------------------------------
def clean_document(doc: Document) -> Document:
    """Cleans metadata for Chroma compatibility."""

    if doc.metadata is None:
        doc.metadata = {}

    safe_meta = {}
    for k, v in doc.metadata.items():
        # Keep simple datatypes
        if isinstance(v, (str, int, float, bool)):
            safe_meta[k] = v
        else:
            safe_meta[k] = str(v)  # convert lists, dicts, None to string

    return Document(
        page_content=doc.page_content,
        metadata=safe_meta
    )


# -------------------------------------------------------
# ADD DOCUMENTS WITH AUTOMATIC BATCHING (fixed)
# -------------------------------------------------------
def add_documents_to_db(vectorstore: Chroma, docs: List[Union[str, Document]], batch_size: int = 160):

    if not docs:
        print("No documents provided.")
        return

    # 1) Convert all items to Document + clean metadata
    clean_docs = []
    for d in docs:

        # Convert string → Document
        if isinstance(d, str):
            d = Document(page_content=d, metadata={})

        # Skip anything invalid
        if not isinstance(d, Document):
            print("Skipping invalid doc:", type(d))
            continue

        clean_docs.append(clean_document(d))

    total = len(clean_docs)
    print(f"Total documents to insert: {total}")

    # 2) Insert in safe batches
    for i in range(0, total, batch_size):
        batch = clean_docs[i:i + batch_size]
        print(f"Adding batch {i//batch_size + 1} with {len(batch)} docs...")
        vectorstore.add_documents(batch)

    print("🎉 All documents successfully added to vector DB.")


