# Specs PDFs contain assembly and quantity information visually,
# but are scanned/layout-based. ERP material master is treated
# as the authoritative structured BOM source.


import json
import re
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
import pdfplumber
from email import policy
from email.parser import BytesParser

# =====================================================
# PATH CONFIGURATION (MATCHES YOUR PROJECT STRUCTURE)
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "hugo_data_samples"
EMAIL_DIR = DATA_DIR / "emails"
SPECS_DIR = DATA_DIR / "specs"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

TODAY = datetime(2025, 4, 20)  # letting the demo be deterministic

print(" Data directory:", DATA_DIR)

# =====================================================
# LOAD CSV DATA
# =====================================================
def normalize_stock_levels(df):
    """
    Normalize stock level column names to canonical schema.
    """
    column_map = {
        "quantity_available": "on_hand",
        "quantity": "on_hand",
        "stock_qty": "on_hand",
        "current_stock": "on_hand"
    }

    for old, new in column_map.items():
        if old in df.columns:
            df = df.rename(columns={old: new})

    return df


def normalize_stock_movements(df):
    """
    Normalize stock movement quantity column.
    """
    column_map = {
        "movement_qty": "quantity",
        "qty": "quantity",
        "change": "quantity"
    }

    for old, new in column_map.items():
        if old in df.columns:
            df = df.rename(columns={old: new})

    return df
def normalize_material_master(df):
    """
    Normalize material master schema:
    - used_in_models → model
    - explode semicolon-separated models
    """

    # Rename to canonical name
    df = df.rename(columns={"used_in_models": "model"})

    # Ensure string type
    df["model"] = df["model"].fillna("").astype(str)

    # Split semicolon-separated models
    df["model"] = df["model"].str.split(";")

    # Explode into one row per (part_id, model)
    df = df.explode("model")

    # Clean whitespace
    df["model"] = df["model"].str.strip()

    # Drop empty rows
    df = df[df["model"] != ""]

    return df

def clean_email_text(text: str) -> str:
    """
    Clean common encoding artifacts from email text.
    """
    if not isinstance(text, str):
        return ""

    # Replace Unicode replacement characters
    text = text.replace("\ufffd", "")

    # Normalize common smart quotes / artifacts
    replacements = {
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "-",
        "\xa0": " "
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    return text.strip()

def load_csv(filename):
    df = pd.read_csv(DATA_DIR / filename)
    df.columns = [c.lower() for c in df.columns]
    return df

material_master = normalize_material_master(load_csv("material_master.csv"))
stock_levels = normalize_stock_levels(load_csv("stock_levels.csv"))
stock_movements = normalize_stock_movements(load_csv("stock_movements.csv"))
material_orders = load_csv("material_orders.csv")
sales_orders = load_csv("sales_orders.csv")
suppliers = load_csv("suppliers.csv")
dispatch_params = load_csv("dispatch_parameters.csv")
print("Stock Levels Columns:", stock_levels.columns.tolist())
print("Stock Movements Columns:", stock_movements.columns.tolist())


# =====================================================
# EMAIL PARSING
# =====================================================

def parse_email(path: Path):
    with open(path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode(
                    part.get_content_charset() or "utf-8",
                    errors="replace"
                )
                break
    else:
        body = msg.get_payload(decode=True).decode(
            msg.get_content_charset() or "utf-8",
            errors="replace"
        )

    return {
        "subject": msg["subject"] or "",
        "from": msg["from"],
        "date": msg["date"],
        "body": body
    }

def classify_email(text: str):
    t = text.lower()
    if "delay" in t:
        return "delay"
    if "price" in t:
        return "price_update"
    if "discount" in t:
        return "discount"
    if "cancel" in t:
        return "cancellation"
    if "discontinu" in t:
        return "discontinuation"
    if "quality" in t:
        return "quality_alert"
    if "proposal" in t:
        return "proposal"
    if "partial shipment" in t:
        return "partial_shipment"
    if "framework" in t:
        return "contract_change"
    return "informational"

email_events = []

for eml_file in EMAIL_DIR.glob("*.eml"):
    parsed = parse_email(eml_file)

    clean_body = clean_email_text(parsed["body"])
    clean_subject = clean_email_text(parsed["subject"])

    email_events.append({
        "event_type": classify_email(clean_subject + clean_body),
        "subject": clean_subject,
        "source": parsed["from"],
        "date": parsed["date"],
        "confidence": "high",
        "raw_text": clean_body
    })


with open(OUTPUT_DIR / "email_events.json", "w") as f:
    json.dump(email_events, f, indent=2)

print(" Emails processed")

# =====================================================
# SPECS PARSING (pdfplumber)
# =====================================================

BOM_PATTERN = re.compile(
    r"(P\d{3})\s+(.+?)\s+(\d+)(?:\s+.*)?$"
)

specs_bom = []
assembly_constraints = []

for pdf_file in SPECS_DIR.glob("*.pdf"):
    model = pdf_file.stem.replace("scanned_", "").replace("_specs", "")
    text_lines = []

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_lines.extend(text.splitlines())

    # BOM extraction
    for line in text_lines:
        match = BOM_PATTERN.search(line)
        if match:
            specs_bom.append({
                "model": model,
                "part_id": match.group(1),
                "part_name": match.group(2).strip(),
                "quantity": int(match.group(3))
            })

    # Assembly constraints
    constraints = [
        line.strip()
        for line in text_lines
        if any(k in line.lower() for k in [
            "torque", "calibrate", "verify",
            "inspect", "seal", "update", "test"
        ])
    ]

    assembly_constraints.append({
        "model": model,
        "constraints": constraints
    })

with open(OUTPUT_DIR / "specs_bom.json", "w") as f:
    json.dump(specs_bom, f, indent=2)

with open(OUTPUT_DIR / "assembly_constraints.json", "w") as f:
    json.dump(assembly_constraints, f, indent=2)

print(" Specs processed")

# =====================================================
# INVENTORY HEALTH METRICS
# =====================================================

consumption = (
    stock_movements
    .groupby("part_id")["quantity"]
    .mean()
    .abs()
    .reset_index(name="avg_daily_consumption")
)

inventory = (
    stock_levels
    .merge(consumption, on="part_id", how="left")
    .merge(dispatch_params, on="part_id", how="left")
    .fillna(0)
)

inventory["days_of_cover"] = inventory.apply(
    lambda r: r["on_hand"] / r["avg_daily_consumption"]
    if r["avg_daily_consumption"] > 0 else np.inf,
    axis=1
)

with open(OUTPUT_DIR / "part_inventory_health.json", "w") as f:
    json.dump(inventory.to_dict(orient="records"), f, indent=2)

print(" Inventory health computed")

# =====================================================
# MODEL DEPENDENCIES (FROM MATERIAL MASTER – AUTHORITATIVE)
# =====================================================

model_dependencies = (
    material_master
    .groupby("model")["part_id"]
    .apply(list)
    .reset_index()
    .to_dict(orient="records")
)

with open(OUTPUT_DIR / "model_dependencies.json", "w") as f:
    json.dump(model_dependencies, f, indent=2)

print(" Model dependencies derived from material master")


with open(OUTPUT_DIR / "model_dependencies.json", "w") as f:
    json.dump(model_dependencies, f, indent=2)

# =====================================================
# OPERATIONAL SNAPSHOT (LLM READY)
# =====================================================

open_pos = material_orders[material_orders["status"] == "open"]
snapshot = []

for _, row in inventory.iterrows():
    part_id = row["part_id"]

    pos = open_pos[open_pos["part_id"] == part_id]
    next_arrival = None
    if not pos.empty:
        next_arrival = min(
            (pd.to_datetime(pos["expected_date"]) - TODAY).dt.days
        )

    used_in_models = [
        b["model"] for b in specs_bom if b["part_id"] == part_id
    ]

    snapshot.append({
        "part_id": part_id,
        "on_hand": row["on_hand"],
        "avg_daily_consumption": round(row["avg_daily_consumption"], 2),
        "days_of_cover": round(row["days_of_cover"], 2),
        "safety_stock": row.get("safety_stock"),
        "next_po_arrival_days": next_arrival,
        "used_in_models": used_in_models,
        "risk_flags": [
            "stockout_risk" if row["days_of_cover"] < 5 else None
        ]
    })

with open(OUTPUT_DIR / "operational_snapshot.json", "w") as f:
    json.dump(snapshot, f, indent=2)

print(" FULL DATA PREPROCESSING COMPLETE")
