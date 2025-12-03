import os

from app.rag.rulebook_loader import load_rulebook
from app.rag.template_loader import load_template_excel
from app.rag.rulebook_chunker import chunk_rulebook
from app.rag.template_chunker import chunk_template_excel
from app.rag.embedder import get_embedder
from app.rag.vector_db import create_vector_db, add_documents_to_db
from app.rag.retriever import get_combined_retriever
from app.rag.prompt_builder import get_regulatory_prompt
from app.rag.rag_pipeline import (
    build_combined_rag,
)
from langchain_openai import ChatOpenAI


# CONFIG
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RULEBOOK_PATH = os.path.join(BASE_DIR, "data", "Liquidity Coverage Ratio (CRR)_26-11-2025.pdf")
TEMPLATE_PATH = os.path.join(BASE_DIR, "data", "Annex XXIV - LCR templates_for publication.xlsx")
PERSIST_DIR = os.path.join(BASE_DIR, "chroma_pra_lcr_db")


# MAIN PIPELINE
def build_pipeline():

    print("Loading Rulebook PDF...")
    rulebook_docs_raw = load_rulebook(RULEBOOK_PATH)
    print(f"Loaded {len(rulebook_docs_raw)} pages.")

    print("Chunking Rulebook...")
    rulebook_chunks = chunk_rulebook(rulebook_docs_raw)
    print(f"Rulebook chunks: {len(rulebook_chunks)}")

    print("Loading Template Excel...")
    xls = load_template_excel(TEMPLATE_PATH)

    print("Chunking Template...")
    template_docs = chunk_template_excel(xls)
    print(f"Template rows converted to docs: {len(template_docs)}")

    print("Initializing Embedder...")
    embeddings = get_embedder()

    print("Creating Vector Database...")
    vectorstore = create_vector_db(
        embeddings=embeddings,
        persist_dir=PERSIST_DIR,
        collection_name="pra_lcr_collection",
        fresh=True
    )

    print("Adding Rulebook docs to Vector DB...")
    add_documents_to_db(vectorstore, rulebook_chunks)

    print("Adding Template docs to Vector DB...")
    add_documents_to_db(vectorstore, template_docs)

    print("Initializing LLM...")
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.0)

    print("Loading Regulatory Prompt...")
    prompt = get_regulatory_prompt()

    print("Creating Retriever...")
    combined_retriever = get_combined_retriever(vectorstore)

    print("Building RAG Chains...")
    combined_rag = build_combined_rag(combined_retriever, llm, prompt)

    print("Pipeline successfully built.\n")

    return {
        "vectorstore": vectorstore,
        "combined_rag": combined_rag,
        "retriever": combined_retriever,
        "llm": llm,
        "prompt": prompt
    }

def demo_query(pipeline, question: str):
    rag = pipeline["combined_rag"]

    print(f"Question: {question}\n")

    answer = rag.invoke(question)
    print("Answer:\n")
    print(answer)
    print("\n" + "="*80)


# RUN PIPELINE
if __name__ == "__main__":
    pipeline = build_pipeline()

    # Example queries
    demo_query(pipeline, "What is the definition of HQLA?")
    demo_query(pipeline, "Where do I report Level 1 assets?")
    demo_query(pipeline, "What does Article 2 say?")