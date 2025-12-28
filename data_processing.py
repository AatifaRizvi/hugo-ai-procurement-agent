# =============================================
# Hugo Agent - Final Safe Version
# =============================================

import json
import re
from pathlib import Path
from datetime import datetime
import os

import pandas as pd
import numpy as np
import pdfplumber
from email import policy
from email.parser import BytesParser

# -----------------------------
# PATH CONFIGURATION
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "hugo_data_samples"
EMAIL_DIR = DATA_DIR / "emails"
SPECS_DIR = DATA_DIR / "specs"
OUTPUT_DIR = BASE_DIR / "outputs"

# Ensure output folder exists
OUTPUT_DIR.mkdir(exist_ok=True)

SNAPSHOT_FILE = OUTPUT_DIR / "operational_snapshot.json"
TODAY = datetime(2025, 4, 20)  # deterministic date for demo

print("Data directory:", DATA_DIR)

# -----------------------------
# SAFE JSON LOADER
# -----------------------------
def load_json(path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# -----------------------------
# CSV LOADERS & NORMALIZATION
# -----------------------------
def load_csv(filename):
    df = pd.read_csv(DATA_DIR / filename)
    df.columns = [c.lower() for c in df.columns]
    return df

def normalize_stock_levels(df):
    column_map = {"quantity_available": "on_hand",
                  "quantity": "on_hand",
                  "stock_qty": "on_hand",
                  "current_stock": "on_hand"}
    for old, new in column_map.items():
        if old in df.columns:
            df.rename(columns={old: new}, inplace=True)
    return df

def normalize_stock_movements(df):
    column_map = {"movement_qty": "quantity",
                  "qty": "quantity",
                  "change": "quantity"}
    for old, new in column_map.items():
        if old in df.columns:
            df.rename(columns={old: new}, inplace=True)
    return df

def normalize_material_master(df):
    df = df.rename(columns={"used_in_models": "model"})
    df["model"] = df["model"].fillna("").astype(str).str.split(";")
    df = df.explode("model")
    df["model"] = df["model"].str.strip()
    df = df[df["model"] != ""]
    return df

# -----------------------------
# EMAIL PARSING
# -----------------------------
def clean_email_text(text):
    if not isinstance(text, str): return ""
    text = text.replace("\ufffd", "")
    replacements = {"’":"'", "‘":"'", "“":'"', "”":'"', "–":"-", "—":"-", "\xa0":" "}
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text.strip()

def parse_email(path: Path):
    with open(path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode(
                    part.get_content_charset() or "utf-8", errors="replace")
                break
    else:
        body = msg.get_payload(decode=True).decode(
            msg.get_content_charset() or "utf-8", errors="replace")
    return {"subject": msg["subject"] or "",
            "from": msg["from"],
            "date": msg["date"],
            "body": body}

def classify_email(text):
    t = text.lower()
    mapping = [("delay","delay"),
               ("price","price_update"),
               ("discount","discount"),
               ("cancel","cancellation"),
               ("discontinu","discontinuation"),
               ("quality","quality_alert"),
               ("proposal","proposal"),
               ("partial shipment","partial_shipment"),
               ("framework","contract_change")]
    for k, v in mapping:
        if k in t: return v
    return "informational"

# -----------------------------
# RUN HUGO FUNCTION
# -----------------------------
def run_hugo():
    # Load CSVs
    material_master = normalize_material_master(load_csv("material_master.csv"))
    stock_levels = normalize_stock_levels(load_csv("stock_levels.csv"))
    stock_movements = normalize_stock_movements(load_csv("stock_movements.csv"))
    material_orders = load_csv("material_orders.csv")
    sales_orders = load_csv("sales_orders.csv")
    suppliers = load_csv("suppliers.csv")
    dispatch_params = load_csv("dispatch_parameters.csv")

    print("Stock Levels Columns:", stock_levels.columns.tolist())
    print("Stock Movements Columns:", stock_movements.columns.tolist())

    # -----------------------------
    # Emails
    # -----------------------------
    email_events = []
    for eml_file in EMAIL_DIR.glob("*.eml"):
        parsed = parse_email(eml_file)
        clean_body = clean_email_text(parsed["body"])
        clean_subject = clean_email_text(parsed["subject"])
        email_events.append({"event_type": classify_email(clean_subject + clean_body),
                             "subject": clean_subject,
                             "source": parsed["from"],
                             "date": parsed["date"],
                             "confidence": "high",
                             "raw_text": clean_body})
    with open(OUTPUT_DIR / "email_events.json", "w") as f:
        json.dump(email_events, f, indent=2)
    print("Emails processed")

    # -----------------------------
    # Specs parsing
    # -----------------------------
    BOM_PATTERN = re.compile(r"(P\d{3})\s+(.+?)\s+(\d+)(?:\s+.*)?$")
    specs_bom = []
    assembly_constraints = []
    for pdf_file in SPECS_DIR.glob("*.pdf"):
        model = pdf_file.stem.replace("scanned_", "").replace("_specs", "")
        text_lines = []
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t: text_lines.extend(t.splitlines())
        for line in text_lines:
            m = BOM_PATTERN.search(line)
            if m: specs_bom.append({"model": model,
                                    "part_id": m.group(1),
                                    "part_name": m.group(2).strip(),
                                    "quantity": int(m.group(3))})
        constraints = [line.strip() for line in text_lines if any(k in line.lower() for k in ["torque","calibrate","verify","inspect","seal","update","test"])]
        assembly_constraints.append({"model": model, "constraints": constraints})
    with open(OUTPUT_DIR / "specs_bom.json", "w") as f: json.dump(specs_bom, f, indent=2)
    with open(OUTPUT_DIR / "assembly_constraints.json", "w") as f: json.dump(assembly_constraints, f, indent=2)
    print("Specs processed")

    # -----------------------------
    # Inventory health
    # -----------------------------
    consumption = stock_movements.groupby("part_id")["quantity"].mean().abs().reset_index(name="avg_daily_consumption")
    inventory = stock_levels.merge(consumption,on="part_id",how="left").merge(dispatch_params,on="part_id",how="left").fillna(0)
    inventory["days_of_cover"] = inventory.apply(lambda r: r["on_hand"]/r["avg_daily_consumption"] if r["avg_daily_consumption"]>0 else np.inf, axis=1)
    with open(OUTPUT_DIR / "part_inventory_health.json","w") as f: json.dump(inventory.to_dict(orient="records"), f, indent=2)
    print("Inventory health computed")

    # -----------------------------
    # Model dependencies
    # -----------------------------
    model_dependencies = material_master.groupby("model")["part_id"].apply(list).reset_index().to_dict(orient="records")
    with open(OUTPUT_DIR / "model_dependencies.json","w") as f: json.dump(model_dependencies,f,indent=2)
    print("Model dependencies derived from material master")

    # -----------------------------
    # Operational snapshot (LLM ready)
    # -----------------------------
    open_pos = material_orders[material_orders["status"]=="open"]
    snapshot = []
    for _, row in inventory.iterrows():
        part_id = row["part_id"]
        pos = open_pos[open_pos["part_id"]==part_id]
        next_arrival = None
        if not pos.empty:
            next_arrival = min((pd.to_datetime(pos["expected_date"]) - TODAY).dt.days)
        used_in_models = [b["model"] for b in specs_bom if b["part_id"]==part_id]
        snapshot.append({"part_id": part_id,
                         "on_hand": row["on_hand"],
                         "avg_daily_consumption": round(row["avg_daily_consumption"],2),
                         "days_of_cover": round(row["days_of_cover"],2),
                         "safety_stock": row.get("safety_stock"),
                         "next_po_arrival_days": next_arrival,
                         "used_in_models": used_in_models,
                         "risk_flags": ["stockout_risk" if row["days_of_cover"]<5 else None]})
    with open(SNAPSHOT_FILE,"w") as f: json.dump(snapshot,f,indent=2)
    print("FULL DATA PREPROCESSING COMPLETE")

# -----------------------------
# RUN
# -----------------------------
if __name__=="__main__":
    run_hugo()
