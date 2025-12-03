from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from app.rag.formatter import format_docs


def build_rag_chain(retriever, llm, prompt):
    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain

def build_combined_rag(retriever, llm, prompt):
    return build_rag_chain(retriever, llm, prompt)

# def build_rulebook_rag(retriever, llm, prompt):
#     return build_rag_chain(retriever, llm, prompt)

# def build_template_rag(retriever, llm, prompt):
#     return build_rag_chain(retriever, llm, prompt)