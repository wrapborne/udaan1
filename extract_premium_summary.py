import re
import pandas as pd

# --- For TXT files ---
def extract_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    return parse_summary_text(text)

# --- For PDF files ---
def extract_from_pdf(file_path):
    import fitz  # PyMuPDF
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return parse_summary_text(text)

# --- Shared logic ---
def parse_summary_text(text):
    # Extract month from heading
    month_match = re.search(r"FOR THE MONTH OF (\d{2}/\d{4})", text)
    report_month = month_match.group(1) if month_match else "Unknown"

    pattern = re.compile(
        r"TOTAL FOR AGENT\s*:\s*(\w+).*?PREMIUM\s*:\s*([\d.]+).*?FP Sch\.Prem\s*:\s*([\d.]+).*?FY Sch\.Prem\s*:\s*([\d.]+)",
        re.IGNORECASE
    )
    data = pattern.findall(text)

    df = pd.DataFrame(data, columns=["Agency Code", "total_premium", "fp_sch_prem", "fy_sch_prem"])
    df["Agency Code"] = df["Agency Code"].str.strip().str.upper()
    df["Report Month"] = report_month  # ✅ Add the month as new column
    return df

