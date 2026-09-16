import pandas as pd

INPUT_FILE = "data/gian_nidhi_raw.csv"

df = pd.read_csv(INPUT_FILE, dtype=str).fillna("")

print("=" * 70)
print("GIAN NIDHI DATA VALIDATION")
print("=" * 70)

print(f"\nRaw rows: {len(df)}")
print(f"Unique IDs: {df['id'].nunique()}")
print(f"Unique Sr Nos: {df['sr_no'].nunique()}")

# Check exact duplicate rows
data_columns = [
    "id",
    "column_status",
    "sr_no",
    "project_name",
    "participants",
    "abstract",
    "college_status",
]

exact_duplicates = df.duplicated(
    subset=data_columns,
    keep=False
)

print(f"\nRows belonging to exact duplicate groups: "
      f"{exact_duplicates.sum()}")

print(f"Exact duplicate rows after keeping one copy: "
      f"{df.duplicated(subset=data_columns).sum()}")

# Check whether each ID occurs exactly twice
id_counts = df["id"].value_counts()

print("\nID frequency distribution:")
print(id_counts.value_counts().sort_index())

# IDs where rows are NOT exactly identical
different_ids = []

for record_id, group in df.groupby("id", sort=False):

    unique_versions = group[data_columns].drop_duplicates()

    if len(unique_versions) > 1:
        different_ids.append(record_id)

print(
    f"\nIDs having different data between repeated rows: "
    f"{len(different_ids)}"
)

if different_ids:
    print("\nThese IDs require investigation:")
    print(different_ids[:100])

    print("\nExample differing records:")

    example_id = different_ids[0]

    print(
        df[df["id"] == example_id][data_columns]
        .to_string(index=False)
    )

else:
    print(
        "\nSUCCESS: Every repeated ID contains identical data."
    )

# Check missing values
print("\nMissing values by column:")
print(df[data_columns].replace("", pd.NA).isna().sum())

# Check IDs
numeric_ids = pd.to_numeric(df["id"], errors="coerce")

print("\nID range:")
print("Minimum ID:", numeric_ids.min())
print("Maximum ID:", numeric_ids.max())

expected_ids = set(range(1, 641))
actual_ids = set(numeric_ids.dropna().astype(int))

missing_ids = sorted(expected_ids - actual_ids)
extra_ids = sorted(actual_ids - expected_ids)

print("Missing IDs:", missing_ids)
print("Unexpected IDs:", extra_ids)

print("\n" + "=" * 70)
print("VALIDATION COMPLETE")
print("=" * 70)