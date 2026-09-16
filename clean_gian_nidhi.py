import os
import re
import pandas as pd


# ============================================================
# 1. Configuration
# ============================================================

INPUT_FILE = "data/gian_nidhi_raw.csv"
OUTPUT_FILE = "data/gian_nidhi.csv"


# ============================================================
# 2. Text utilities
# ============================================================

def clean_text(value):
    """
    Normalize whitespace while preserving the actual wording.
    """

    if pd.isna(value):
        return ""

    return " ".join(
        str(value).split()
    ).strip()


def looks_like_long_text(value):
    """
    Detect values that look like an abstract/description
    rather than a college name.

    This is only a structural cleaning rule.
    """

    value = clean_text(value)

    if not value:
        return False

    # Long paragraph
    if len(value) > 200:
        return True

    # Sentence-like text
    if value.count(".") >= 2:
        return True

    return False


def looks_like_person_list(value):
    """
    Conservative check for participant-like text.

    We do NOT use this to invent participants.
    It is only used to identify obviously suspicious
    project-name-as-participant cases.
    """

    value = clean_text(value)

    if not value:
        return False

    # A participant field normally contains names separated
    # by commas. This is deliberately conservative.
    if "," in value:
        return True

    return False


# ============================================================
# 3. Load raw data
# ============================================================

print("=" * 70)
print("GIAN NIDHI DATA CLEANING")
print("=" * 70)

print()

print("Input:")
print(INPUT_FILE)

print()

df = pd.read_csv(
    INPUT_FILE,
    dtype=str,
    keep_default_na=False
)

print(
    "Raw rows:",
    len(df)
)


# ============================================================
# 4. Normalize text
# ============================================================

text_columns = [
    "id",
    "column_status",
    "sr_no",
    "project_name",
    "participants",
    "abstract",
    "college_status"
]

for column in text_columns:

    df[column] = (
        df[column]
        .apply(clean_text)
    )


# ============================================================
# 5. Remove exact duplicate rows
# ============================================================

before_duplicates = len(df)

df = df.drop_duplicates(
    subset=[
        "id",
        "column_status",
        "sr_no",
        "project_name",
        "participants",
        "abstract",
        "college_status"
    ],
    keep="first"
).copy()

duplicates_removed = (
    before_duplicates - len(df)
)

print(
    "Exact duplicate rows removed:",
    duplicates_removed
)


# ============================================================
# 6. Rule-based field corrections
# ============================================================

corrections = []


# ------------------------------------------------------------
# Rule A:
# Abstract empty + college contains long paragraph
#
# Move the paragraph to abstract and leave college blank.
# ------------------------------------------------------------

for index, row in df.iterrows():

    abstract = row["abstract"]
    college = row["college_status"]

    if (
        not abstract
        and looks_like_long_text(college)
    ):

        corrections.append({
            "id": row["id"],
            "field": "college_status -> abstract",
            "reason": (
                "Abstract field empty while college field "
                "contains paragraph-like project description."
            )
        })

        df.at[
            index,
            "abstract"
        ] = college

        df.at[
            index,
            "college_status"
        ] = ""


# ------------------------------------------------------------
# Rule B:
# Participants exactly equal project name
#
# Do not treat project name as a participant.
# Leave participants blank because source does not provide
# a usable participant value in that field.
# ------------------------------------------------------------

for index, row in df.iterrows():

    participants = clean_text(
        row["participants"]
    )

    project_name = clean_text(
        row["project_name"]
    )

    if (
        participants
        and project_name
        and participants.lower()
        == project_name.lower()
    ):

        corrections.append({
            "id": row["id"],
            "field": "participants",
            "reason": (
                "Participant field exactly matches project name; "
                "not treated as a person."
            )
        })

        df.at[
            index,
            "participants"
        ] = ""


# ============================================================
# 7. Ensure one record per project ID
# ============================================================

# At this point exact duplicates should already be removed.

duplicate_ids = df[
    df["id"].duplicated(
        keep=False
    )
]["id"].unique()

print()

print(
    "Duplicate IDs remaining:",
    len(duplicate_ids)
)

if len(duplicate_ids) > 0:

    print(
        "WARNING: Some IDs still have multiple records."
    )

    print(
        duplicate_ids[:50]
    )


# ============================================================
# 8. Add stable record ID
# ============================================================

df["record_id"] = (
    df["id"]
    .apply(
        lambda x: f"GN-{int(x):03d}"
    )
)


# ============================================================
# 9. Reorder columns
# ============================================================

df = df[
    [
        "record_id",
        "id",
        "column_status",
        "sr_no",
        "project_name",
        "participants",
        "abstract",
        "college_status",
        "source",
        "source_url",
        "data_category"
    ]
]


# ============================================================
# 10. Save cleaned CSV
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 11. Validation
# ============================================================

print()

print("=" * 70)
print("CLEANING COMPLETE")
print("=" * 70)

print()

print(
    "Cleaned rows:",
    len(df)
)

print(
    "Unique IDs:",
    df["id"].nunique()
)

print(
    "Unique record IDs:",
    df["record_id"].nunique()
)

print(
    "Corrections applied:",
    len(corrections)
)


# ============================================================
# 12. Missing values
# ============================================================

print()

print("=" * 70)
print("MISSING VALUE SUMMARY")
print("=" * 70)

print()

for column in [
    "participants",
    "abstract",
    "college_status"
]:

    missing = (
        df[column]
        .fillna("")
        .astype(str)
        .str.strip()
        .eq("")
        .sum()
    )

    print(
        f"{column:20s}: {missing}"
    )


# ============================================================
# 13. Known record verification
# ============================================================

print()

print("=" * 70)
print("KNOWN RECORD VERIFICATION")
print("=" * 70)

print()

check_ids = [
    "171",
    "173",
    "426",
    "429"
]

check_df = df[
    df["id"].isin(
        check_ids
    )
]

print(
    check_df[
        [
            "record_id",
            "id",
            "project_name",
            "participants",
            "abstract",
            "college_status"
        ]
    ].to_string(
        index=False
    )
)


# ============================================================
# 14. Print cleaning decisions
# ============================================================

print()

print("=" * 70)
print("CLEANING DECISIONS")
print("=" * 70)

print()

if corrections:

    for correction in corrections:

        print(
            f"ID {correction['id']} | "
            f"{correction['field']} | "
            f"{correction['reason']}"
        )

else:

    print(
        "No rule-based corrections were required."
    )


# ============================================================
# 15. Final checks
# ============================================================

print()

print("=" * 70)
print("FINAL VALIDATION")
print("=" * 70)

print()

assert len(df) == 640, (
    f"Expected 640 records, "
    f"found {len(df)}"
)

assert df["id"].nunique() == 640, (
    "Project IDs are not unique."
)

assert df["record_id"].nunique() == 640, (
    "Record IDs are not unique."
)

print(
    "640 unique GIAN Nidhi records confirmed."
)

print()

print(
    f"Saved cleaned dataset to: {OUTPUT_FILE}"
)

print()

print("=" * 70)
print("DATA CLEANING SUCCESSFUL")
print("=" * 70)