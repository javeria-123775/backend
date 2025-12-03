from langchain_chroma import Chroma

DEFAULT_K = 6
DEFAULT_FETCH_K = 20

def get_combined_retriever(
    vectorstore: Chroma,
    k: int = DEFAULT_K,
    fetch_k: int = DEFAULT_FETCH_K,
):
    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": k,
            "fetch_k": fetch_k,
        },
    )

# def get_rulebook_retriever(
#     vectorstore: Chroma,
#     k: int = DEFAULT_K,
#     fetch_k: int = DEFAULT_FETCH_K,
# ):
#     return vectorstore.as_retriever(
#         search_type="mmr",
#         search_kwargs={
#             "k": k,
#             "fetch_k": fetch_k,
#             "filter": {"doc_type": "pra_rulebook"},
#         },
#     )


# def get_template_retriever(
#     vectorstore: Chroma,
#     k: int = DEFAULT_K,
#     fetch_k: int = DEFAULT_FETCH_K,
# ):
#     return vectorstore.as_retriever(
#         search_type="mmr",
#         search_kwargs={
#             "k": k,
#             "fetch_k": fetch_k,
#             "filter": {"doc_type": "lcr_template"},
#         },
#     )

