import pandas as pd
from datetime import datetime

def format_date(date_str):
    """Converts date from YYYYMMDD to DD/MM/YYYY format."""
    try:
        if date_str and len(date_str) == 8 and date_str.isdigit():
            return datetime.strptime(date_str, "%Y%m%d").strftime("%d/%m/%Y")
        return date_str
    except Exception:
        return date_str

def get_enach_date(doc_str, mode_str):
    """Determines ENACH debit date based on DOC and mode."""
    try:
        if not doc_str or not mode_str or mode_str.strip().lower() not in ["m", "mly", "monthly", "month", "monthly mode"]:
            return ""

        doc = datetime.strptime(doc_str, "%d/%m/%Y")
        day = doc.day

        if 1 <= day <= 7:
            return "7"
        elif 8 <= day <= 15:
            return "15"
        elif 16 <= day <= 22:
            return "22"
        elif 23 <= day <= 31:
            return "28"
        return ""
    except Exception as e:
        print(f"[ENACH ERROR] DOC: {doc_str}, Mode: {mode_str}, Error: {e}")
        return ""

def extract_all_lic_data(file_path):
    """Parses LIC text file and extracts relevant policy data into a DataFrame."""
    data = []

    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    i = 0
    current_agent_name = ""
    current_agency_code = ""

    while i < len(lines):
        line = lines[i].strip()

        # Capture agent name
        if "Name of the agent" in line:
            current_agent_name = line.split("Name of the agent")[-1].strip().lstrip(":").strip()

        # Capture agency code
        elif "Agency Code No." in line:
            parts = line.split(":")
            if len(parts) > 1:
                current_agency_code = parts[1].strip()

        parts = line.split('|')

        if len(parts) > 6 and parts[1].strip().isdigit():
            try:
                next_line = lines[i + 1].strip().split('|') if i + 1 < len(lines) else []

                # Extract fields from main line
                proposal_date = format_date(parts[0].strip())
                proposal_no = parts[1].strip().lstrip("0")
                short_name = parts[2].strip()
                date_of_completion = format_date(parts[5].strip())
                policy_no = parts[6].strip()
                plan = parts[9].strip() if len(parts) > 9 else ""
                mode = parts[10].strip() if len(parts) > 10 else ""
                premium = parts[11].strip() if len(parts) > 11 else ""
                remarks = parts[12].strip() if len(parts) > 12 else ""

                # Extract from next line
                doc = format_date(next_line[6].strip()) if len(next_line) > 6 else ""
                term = next_line[9].strip() if len(next_line) > 9 else ""

                ananda = "YES" if proposal_no.isdigit() and len(proposal_no) == 6 else ""
                enach_date = get_enach_date(doc, mode)

                data.append({
                    "Agent Name": current_agent_name,
                    "Agency Code": current_agency_code,
                    "Date of Proposal": proposal_date,
                    "Proposal No": proposal_no,
                    "Short Name": short_name,
                    "Policy No": policy_no,
                    "Date of Completion": date_of_completion,
                    "DOC": doc,
                    "Plan": plan,
                    "Term": term,
                    "Mode": mode,
                    "Premium": premium,
                    "Remarks": remarks,
                    "ANANDA": ananda,
                    "ENACH Date": enach_date,
                })

            except Exception as e:
                print(f"[ERROR] Failed to parse line {i}: {e}")

            i += 2  # Skip next line since it’s already processed
        else:
            i += 1  # Continue to next line

    # Create DataFrame and remove rows without valid Policy No
    df = pd.DataFrame(data)
    df = df[df["Policy No"].astype(str).str.strip() != ""]
    return df
