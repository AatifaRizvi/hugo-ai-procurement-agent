import os
import pandas as pd
import pdfplumber
import json

# --------------------------
# Folders
# --------------------------
RAW_DIR = r"C:\Users\hp\Documents\HUGO_DRYFT\data\hugo_data_samples"
PROCESSED_DIR = r"C:\Users\hp\Documents\HUGO_DRYFT\data\processed_data"

os.makedirs(PROCESSED_DIR, exist_ok=True)

# --------------------------
# Process material_master.csv
# --------------------------
erp_file = os.path.join(RAW_DIR, "material_master.csv")
erp_df = pd.read_csv(erp_file)

# Optional: remove duplicates
erp_df.drop_duplicates(inplace=True)

# Save processed material master
erp_df.to_csv(os.path.join(PROCESSED_DIR, "erp_processed.csv"), index=False)
print(f"Processed material_master.csv → {PROCESSED_DIR}/erp_processed.csv")

# --------------------------
# Process orders.csv (optional)
# --------------------------
orders_file = os.path.join(RAW_DIR, "orders.csv")
if os.path.exists(orders_file):
    orders_df = pd.read_csv(orders_file)
    orders_df.to_csv(os.path.join(PROCESSED_DIR, "orders_processed.csv"), index=False)
    print(f"Processed orders.csv → {PROCESSED_DIR}/orders_processed.csv")
else:
    print("Orders CSV not found, skipping orders processing.")

# --------------------------
# Process BOM/Specs PDFs
# --------------------------
boms = []
bom_folder = os.path.join(RAW_DIR, "specs")  # updated folder path
if os.path.exists(bom_folder):
    for pdf_file in os.listdir(bom_folder):
        if pdf_file.lower().endswith(".pdf"):
            pdf_path = os.path.join(bom_folder, pdf_file)
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                boms.append({"file": pdf_file, "text": text})

    # Save as JSON
    with open(os.path.join(PROCESSED_DIR, "boms_processed.json"), "w", encoding="utf-8") as f:
        json.dump(boms, f, indent=2, ensure_ascii=False)
    print(f"Processed {len(boms)} PDFs → {PROCESSED_DIR}/boms_processed.json")
else:
    print("Specs folder not found, skipping PDF processing.")

print("Data processing complete! ✅")
