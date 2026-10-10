"""Small helpers shared by the project's scripts."""
import csv
from datetime import date, datetime
from pathlib import Path

# src/loan_model/common.py -> parents[2] is the project root
DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def read_csv(path):
    """Return (column_names, rows). Every cell is a stripped string."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            rows.append({k: (v or "").strip() for k, v in row.items() if k is not None})
        return reader.fieldnames or [], rows


def check_date(text):
    """Return an error message if text is not a valid past/today date, else None."""
    try:
        parsed = datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        return "date must look like YYYY-MM-DD"
    if parsed > date.today():
        return "date is in the future"
    return None
