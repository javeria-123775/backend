import pandas as pd

def load_template_excel(excel_path: str) -> pd.ExcelFile:

    xls = pd.ExcelFile(excel_path)
    return xls