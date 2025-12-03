from app.rag.main import build_pipeline

class RAGPipelineService:
    def __init__(self):
        print("⚙️ Building full RAG pipeline...")
        self.pipeline = build_pipeline()
        self.rag = self.pipeline["combined_rag"]
        self.retriever = self.pipeline["retriever"]   # ⭐ Needed for metadata

    def query(self, question: str, history=None):
        """
        Returns: answer_text, metadata_list
        """

        # ⭐ First: retrieve documents with metadata
        retrieved_docs = self.retriever.invoke(question)

        metadata_list = []
        for doc in retrieved_docs:
            md = doc.metadata.copy()

            metadata_list.append({
                "return": md.get("template_code") or "",
                "sheet": md.get("template_sheet") or "",
                "line_code": md.get("row") or "",
                "line_desc": md.get("id_hierarchy") or "",
                "doc_type": md.get("doc_type"),
                "chapter": md.get("chapter"),
                "title": md.get("title"),
                "article": md.get("article"),
                "section": md.get("section"),
                "subsection": md.get("subsection"),
                "page": md.get("page"),
            })

        # ⭐ Now generate answer using RAG chain
        answer = self.rag.invoke(question)

        return answer, metadata_list


# Global instance for FastAPI
rag_pipeline = RAGPipelineService()


