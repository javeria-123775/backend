def format_docs(docs):
    formatted = []

    for d in docs:
        md = d.metadata
        ref_parts = []

        # Rulebook metadata
        if md.get("chapter"):
            ref_parts.append(f"Chapter: {md['chapter']}")
        if md.get("title"):
            ref_parts.append(f"Title: {md['title']}")
        if md.get("article"):
            ref_parts.append(f"Article: {md['article']}")
        if md.get("section"):
            ref_parts.append(f"Section: {md['section']}")
        if md.get("subsection"):
            ref_parts.append(f"Subsection: {md['subsection']}")
        if md.get("page") is not None:
            ref_parts.append(f"Page: {md['page']}")

        # Template metadata
        if md.get("template_sheet"):
            ref_parts.append(f"Sheet: {md['template_sheet']}")
        if md.get("row"):
            ref_parts.append(f"Row: {md['row']}")
        if md.get("id_hierarchy"):
            ref_parts.append(f"ID: {md['id_hierarchy']}")

        # Source type
        if md.get("doc_type"):
            ref_parts.append(f"Source: {md['doc_type']}")

        header = " | ".join(ref_parts)

        formatted.append(f"[{header}]\n{d.page_content}")

    return "\n\n---\n\n".join(formatted)