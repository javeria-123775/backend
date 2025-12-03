import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

# REGEX PATTERNS
chapter_re = re.compile(r"^\s*((Chapter|CHAPTER)\s*\d+|\d+\s+[A-Z][A-Za-z].+)$")
title_re   = re.compile(r"^\s*(Title|TITLE)\s*[IVXLC0-9]+(\s+.*)?$")
article_re = re.compile(r"^\s*Article\s+\d+", re.IGNORECASE)

section_re = re.compile(r"^\s*(\d+(?:\.\d+)*)(?:\.?)\s+")
subsection_re = re.compile(r"^\s*\([a-z]\)\s+", re.IGNORECASE)
roman_re = re.compile(r"^\s*\((i|ii|iii|iv|v|vi|vii|viii|ix|x)\)\s+", re.IGNORECASE)
date_re = re.compile(r"\b\d{2}/\d{2}/\d{4}\b")

# GLOBAL METADATA
GLOBAL_METADATA = {
    "document_title": "PRA Rulebook – Liquidity Coverage Ratio (CRR)",
    "issuer": "Bank of England",
    "authority": "Prudential Regulation Authority",
    "part": "Liquidity Coverage Ratio (CRR)"
}

# METADATA CLEANING 
def clean_metadata(md):
    clean = {}
    for k, v in md.items():
        if isinstance(v, (list, dict)):
            clean[k] = str(v)
        else:
            clean[k] = v
    return clean


def chunk_rulebook(documents):
    structured_chunks = []

    # State variables
    current_chapter    = None
    current_title      = None
    current_article    = None
    current_section    = None
    current_subsection = None
    current_roman      = []

    # ---- Helper ----
    def push_chunk(buffer, page_num):
        if buffer.strip():
            metadata = {
                **GLOBAL_METADATA,
                "chapter":    current_chapter,
                "title":      current_title,
                "article":    current_article,
                "section":    current_section,
                "subsection": current_subsection,
                "roman":      current_roman.copy(),
                "page":       page_num,
            }
            structured_chunks.append({"text": buffer.strip(), "metadata": metadata})

    # STRUCTURAL CHUNKING
    for doc in documents:
        page_num = doc.metadata.get("page")
        lines = doc.page_content.split("\n")

        buffer = ""

        for line in lines:
            raw = line.strip()
            cleaned = date_re.sub("", raw)
            cleaned = " ".join(cleaned.split())

            if not cleaned or cleaned in ["-", "–", "—"]:
                continue

            # Chapter
            if chapter_re.match(cleaned):
                push_chunk(buffer, page_num)
                buffer = ""
                current_chapter = cleaned
                current_title = current_article = current_section = current_subsection = None
                current_roman = []
                continue

            # Title
            if title_re.match(cleaned):
                push_chunk(buffer, page_num)
                buffer = ""
                current_title = cleaned
                current_article = current_section = current_subsection = None
                current_roman = []
                continue

            # Article
            if article_re.match(cleaned):
                push_chunk(buffer, page_num)
                buffer = ""
                current_article = cleaned
                current_section = current_subsection = None
                current_roman = []
                continue

            # Section
            m_section = section_re.match(cleaned)
            if m_section:
                push_chunk(buffer, page_num)
                buffer = ""
                current_section = m_section.group(1)
                current_subsection = None
                current_roman = []
                buffer += cleaned + "\n"
                continue

            # Roman bullet
            if roman_re.match(cleaned):
                current_roman.append(roman_re.match(cleaned).group().strip())
                buffer += cleaned + "\n"
                continue

            # Subsection (a), (b), ...
            if subsection_re.match(cleaned):
                if (
                    buffer.strip().endswith(":")
                    and not section_re.match(cleaned)
                    and not roman_re.match(cleaned)
                ):
                    buffer += cleaned + "\n"
                    current_subsection = f"({cleaned[1]})"
                    current_roman = []
                    continue

                push_chunk(buffer, page_num)
                buffer = ""
                current_subsection = f"({cleaned[1]})"
                current_roman = []
                buffer += cleaned + "\n"
                continue

            # Normal line
            buffer += cleaned + "\n"

        push_chunk(buffer, page_num)

    # CHARACTER CHUNKING
    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    final_chunks = []

    for item in structured_chunks:
        base_md = item["metadata"].copy()
        base_md.pop("roman", None)

        docs = splitter.create_documents([item["text"]], metadatas=[base_md])

        for d in docs:
            romans, seen = [], set()

            for line in d.page_content.split("\n"):
                m = roman_re.match(line.strip())
                if m:
                    tok = m.group(0).strip()
                    if tok not in seen:
                        romans.append(tok)
                        seen.add(tok)

            d.metadata["roman"] = ", ".join(romans) if romans else None

            # Build header
            md = d.metadata
            structural_parts = []

            if md.get("chapter"):    structural_parts.append(f"Chapter: {md['chapter']}")
            if md.get("title"):      structural_parts.append(f"Title: {md['title']}")
            if md.get("article"):    structural_parts.append(f"Article: {md['article']}")
            if md.get("section"):    structural_parts.append(f"Section: {md['section']}")
            if md.get("subsection"): structural_parts.append(f"Subsection: {md['subsection']}")
            if md.get("roman"):      structural_parts.append(f"Roman: {md['roman']}")

            header = "\n".join(structural_parts)
            d.page_content = header + "\n\n" + d.page_content

            final_chunks.append(d)

    # ADD doc_type + SANITIZE METADATA

    for d in final_chunks:
        d.metadata["doc_type"] = "pra_rulebook"
        d.metadata = clean_metadata(d.metadata)

    return final_chunks
