import json
import pandas as pd
from pathlib import Path


DATA_DIR = Path("data")
OUTPUT_FILE = DATA_DIR / "knowledge_base.json"

SOURCE1_URL = (
    "https://drive.google.com/file/d/"
    "1cS7fMCNjoyD1qnZCC5wOwRUDypQVHX0Z/view"
)

SOURCE2_URL = (
    "https://drive.google.com/file/d/"
    "1D0WbXe75Cn1ow9RcPOSAqMGJ9pPFIw-o/view"
)

GIAN_URL = "https://gian.org/gian-nidhi/"


def clean_value(value):
    """Convert pandas values to JSON-safe strings."""
    if pd.isna(value):
        return ""
    return str(value).strip()


def dataframe_to_records(csv_path):
    """Load a CSV and convert every row to a dictionary."""
    df = pd.read_csv(csv_path, dtype=str).fillna("")

    records = []

    for _, row in df.iterrows():
        record = {
            str(column): clean_value(row[column])
            for column in df.columns
        }
        records.append(record)

    return records


def main():

    print("=" * 70)
    print("CREATING STRUCTURED KNOWLEDGE BASE JSON")
    print("=" * 70)

    # ---------------------------------------------------------
    # Source 1
    # ---------------------------------------------------------
    source1 = dataframe_to_records(
        DATA_DIR / "source1_entities.csv"
    )

    print(f"Source 1 entities: {len(source1)}")

    # ---------------------------------------------------------
    # Source 2
    # ---------------------------------------------------------
    source2 = dataframe_to_records(
        DATA_DIR / "source2_entities.csv"
    )

    print(f"Source 2 entities: {len(source2)}")

    # ---------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------
    relationships = dataframe_to_records(
        DATA_DIR / "relationships.csv"
    )

    print(f"Relationships: {len(relationships)}")

    # ---------------------------------------------------------
    # GIAN Nidhi
    # ---------------------------------------------------------
    gian_nidhi = dataframe_to_records(
        DATA_DIR / "gian_nidhi.csv"
    )

    print(f"GIAN Nidhi records: {len(gian_nidhi)}")

    # ---------------------------------------------------------
    # Build final knowledge base
    # ---------------------------------------------------------

    knowledge_base = {
        "project": {
            "name": "GIAN Multi-Source RAG",
            "description": (
                "AI-ready multi-source knowledge base and "
                "retrieval-augmented generation system."
            ),
            "sources": [
                {
                    "source_id": "SOURCE-1",
                    "source_name": "51st Shodhyatra",
                    "source_url": SOURCE1_URL,
                    "source_type": "PDF"
                },
                {
                    "source_id": "SOURCE-2",
                    "source_name": "53rd Shodhyatra",
                    "source_url": SOURCE2_URL,
                    "source_type": "PDF"
                },
                {
                    "source_id": "SOURCE-3",
                    "source_name": "GIAN Nidhi",
                    "source_url": GIAN_URL,
                    "source_type": "Web"
                }
            ]
        },

        "statistics": {
            "source1_entities": len(source1),
            "source2_entities": len(source2),
            "relationships": len(relationships),
            "gian_nidhi_records": len(gian_nidhi),
            "gian_nidhi_unique_records": len(gian_nidhi)
        },

        "data": {
            "source1_entities": source1,
            "source2_entities": source2,
            "relationships": relationships,
            "gian_nidhi": gian_nidhi
        }
    }

    # ---------------------------------------------------------
    # Write JSON
    # ---------------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            knowledge_base,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("=" * 70)
    print("JSON CREATED SUCCESSFULLY")
    print("=" * 70)
    print(f"Output: {OUTPUT_FILE}")
    print(f"Size: {OUTPUT_FILE.stat().st_size:,} bytes")

    # ---------------------------------------------------------
    # Final verification
    # ---------------------------------------------------------

    with open(
        OUTPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        verification = json.load(f)

    assert len(verification["data"]["source1_entities"]) == len(source1)
    assert len(verification["data"]["source2_entities"]) == len(source2)
    assert len(verification["data"]["relationships"]) == len(relationships)
    assert len(verification["data"]["gian_nidhi"]) == len(gian_nidhi)

    print()
    print("VERIFICATION PASSED")
    print("All CSV records are represented in the JSON file.")

if __name__ == "__main__":
    main()