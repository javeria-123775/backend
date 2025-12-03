import pandas as pd
import math
from langchain_core.documents import Document



def clean_value(v):
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    return v

# CLEAN EACH TEMPLATE SHEET
def clean_template_sheet(sheet_name: str, df: pd.DataFrame):
    """
    Detect header row (Row / ID / Item), remove junk,
    fix merged cells, and attach sheet metadata.
    """

    # Remove fully empty rows/cols
    df = df.dropna(how="all", axis=0)
    df = df.dropna(how="all", axis=1)

    # Identify header row
    header_row = None
    for i in range(len(df)):
        vals = df.iloc[i].astype(str).str.lower()
        if "row" in vals.values:
            header_row = i
            break

    if header_row is None:
        print(f"No header detected for sheet {sheet_name}. Skipping.")
        return None

    # Set header row
    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:]

    # Normalize column names
    df.columns = [str(c).strip() for c in df.columns]

    # Ensure required columns exist
    for col in ["Row", "ID", "Item"]:
        if col not in df.columns:
            df[col] = None

    # Add metadata
    df["template_sheet"] = sheet_name
    df["template_code"] = sheet_name

    return df

# MERGE MULTI-LINE ITEMS
def clean_multiline_items(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    merged_rows = []
    buffer = None

    for _, row in df.iterrows():
        row_code = str(row.get("Row", "")).strip()
        id_code = str(row.get("ID", "")).strip()
        item_text = str(row.get("Item", "")).strip()

        is_continuation = (
            (row_code == "" or row_code.lower() == "nan") and
            (id_code == "" or id_code.lower() == "nan") and
            item_text not in ["", "nan"]
        )

        if is_continuation:
            if buffer is not None:
                buffer["Item"] += " " + item_text
            continue

        if buffer is not None:
            merged_rows.append(buffer)

        buffer = row.to_dict()

    if buffer:
        merged_rows.append(buffer)

    return pd.DataFrame(merged_rows)


# ROW SPLITTER → Document objects
def excel_row_splitter(df: pd.DataFrame):
    docs = []

    for _, row in df.iterrows():
        item_text = str(row.get("Item", "")).strip()

        if not item_text or item_text.lower() == "nan":
            continue

        metadata = {
            "template_sheet": clean_value(row.get("template_sheet")),
            "template_code": clean_value(row.get("template_code")),
            "row": clean_value(row.get("Row")),
            "id_hierarchy": clean_value(row.get("ID")),
            "doc_type": "lcr_template",
        }

        # Add all columns 
        for col in df.columns:
            if col != "Item":
                metadata[col] = clean_value(row.get(col))

        docs.append(Document(page_content=item_text, metadata=metadata))

    return docs


# MAIN FUNCTION
def chunk_template_excel(xls: pd.ExcelFile):
    processed_sheets = []

    for sheet in xls.sheet_names:
        # Skip irrelevant sheets
        if sheet.lower() in ["index", "readme", "instructions"]:
            continue

        raw_df = pd.read_excel(xls, sheet_name=sheet, header=None)
        cleaned = clean_template_sheet(sheet, raw_df)

        if cleaned is not None:
            processed_sheets.append(cleaned)

    # Combine sheets
    combined_df = pd.concat(processed_sheets, ignore_index=True)

    # Fix continuation lines
    templates_df = clean_multiline_items(combined_df)

    # Convert to Document objects
    excel_documents = excel_row_splitter(templates_df)

    return excel_documents