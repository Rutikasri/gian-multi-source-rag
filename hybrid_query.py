# ============================================================
# HYBRID QUERY SYSTEM - GIAN NIDHI
# ============================================================

import os
import re
import pandas as pd
import chromadb

from sentence_transformers import SentenceTransformer


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_PATH = os.path.join(
    BASE_DIR,
    "data",
    "gian_nidhi.csv"
)

CHROMA_PATH = os.path.join(
    BASE_DIR,
    "chroma_db"
)


# ============================================================
# 2. SOURCE
# ============================================================

GIAN_SOURCE = "GIAN Nidhi"

GIAN_URL = "https://gian.org/gian-nidhi/"

COLLECTION_NAME = "gian_knowledge"

MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


# ============================================================
# 3. CHECK CSV
# ============================================================

if not os.path.exists(CSV_PATH):

    raise FileNotFoundError(
        f"\nCSV file not found:\n{CSV_PATH}\n\n"
        "Make sure data/gian_nidhi.csv exists."
    )


# ============================================================
# 4. LOAD CSV
# ============================================================

print("=" * 70)
print("LOADING GIAN NIDHI DATA")
print("=" * 70)

gian_df = pd.read_csv(
    CSV_PATH,
    dtype=str,
    keep_default_na=False
)

print(
    f"Records loaded: {len(gian_df)}"
)


# ============================================================
# 5. REQUIRED COLUMNS
# ============================================================

required_columns = [
    "record_id",
    "id",
    "project_name",
    "participants",
    "abstract",
    "college_status",
    "source",
    "source_url",
    "data_category"
]

missing_columns = [
    column
    for column in required_columns
    if column not in gian_df.columns
]

if missing_columns:

    raise ValueError(
        "\nMissing required CSV columns:\n"
        + "\n".join(missing_columns)
    )


# ============================================================
# 6. NORMALIZATION
# ============================================================

def normalize_text(value):

    if value is None:
        return ""

    value = str(value).lower()

    # Convert punctuation to spaces
    value = re.sub(
        r"[^a-z0-9\s]",
        " ",
        value
    )

    # Remove repeated spaces
    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


# ============================================================
# 7. NORMALIZED SEARCH COLUMNS
# ============================================================

gian_df["project_name_norm"] = (
    gian_df["project_name"]
    .apply(normalize_text)
)

gian_df["participants_norm"] = (
    gian_df["participants"]
    .apply(normalize_text)
)

gian_df["college_norm"] = (
    gian_df["college_status"]
    .apply(normalize_text)
)

gian_df["abstract_norm"] = (
    gian_df["abstract"]
    .apply(normalize_text)
)


# ============================================================
# 8. LOAD CHROMADB
# ============================================================

print("\n" + "=" * 70)
print("LOADING CHROMADB")
print("=" * 70)

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

try:

    collection = client.get_collection(
        name=COLLECTION_NAME
    )

except Exception as e:

    raise RuntimeError(
        "\nCould not load ChromaDB collection.\n"
        "Run ingest.py first.\n\n"
        f"Error: {e}"
    )


print(
    "ChromaDB collection loaded successfully."
)

print(
    f"Collection records: {collection.count()}"
)


# ============================================================
# 9. EMBEDDING MODEL
# ============================================================

print("\n" + "=" * 70)
print("LOADING EMBEDDING MODEL")
print("=" * 70)

print(
    f"Model: {MODEL_NAME}"
)

embedding_model = SentenceTransformer(
    MODEL_NAME
)

print(
    "Embedding model loaded."
)


# ============================================================
# 10. STOP WORDS
# ============================================================

STOP_WORDS = {
    "what",
    "is",
    "are",
    "the",
    "a",
    "an",
    "of",
    "for",
    "to",
    "in",
    "on",
    "with",
    "and",
    "or",
    "about",
    "tell",
    "me",
    "give",
    "show",
    "which",
    "who",
    "where",
    "how",
    "does",
    "do",
    "did",
    "can",
    "please",
    "information",
    "details",
    "detail",
    "project",
    "projects",
    "associated",
    "association",
    "related",
    "relation",
    "college",
    "participant",
    "participants",
    "name",
    "named",
    "called",
    "id",
    "number",
    "government",
    "polytechnic"
}


# ============================================================
# 11. MEANINGFUL WORDS
# ============================================================

def meaningful_words(text):

    words = normalize_text(
        text
    ).split()

    return [
        word
        for word in words
        if word not in STOP_WORDS
        and len(word) > 1
    ]


# ============================================================
# 12. EXTRACT PROJECT NAME
# ============================================================

def extract_project_name(question):

    q = normalize_text(
        question
    )

    # --------------------------------------------
    # Common prefixes
    # --------------------------------------------

    prefixes = [

        r"^what is the project named\s+",
        r"^what is the project called\s+",

        r"^what is the\s+",
        r"^what is\s+",

        r"^tell me about the\s+",
        r"^tell me about\s+",

        r"^describe the\s+",
        r"^describe\s+",

        r"^details of the\s+",
        r"^details of\s+",

        r"^details about the\s+",
        r"^details about\s+",

        r"^information about the\s+",
        r"^information about\s+",

        r"^information on the\s+",
        r"^information on\s+",

        r"^who are the participants of\s+",
        r"^who are the participants for\s+"
    ]

    for pattern in prefixes:

        q = re.sub(
            pattern,
            "",
            q
        )

    # --------------------------------------------
    # project named / called
    # --------------------------------------------

    q = re.sub(
        r"^project\s+named\s+",
        "",
        q
    )

    q = re.sub(
        r"^project\s+called\s+",
        "",
        q
    )

    # --------------------------------------------
    # Leading "the"
    # --------------------------------------------

    q = re.sub(
        r"^the\s+",
        "",
        q
    )

    # --------------------------------------------
    # Remove project at end
    # --------------------------------------------

    q = re.sub(
        r"\s+project$",
        "",
        q
    )

    # --------------------------------------------
    # Remove project at beginning
    # --------------------------------------------

    q = re.sub(
        r"^project\s+",
        "",
        q
    )

    # --------------------------------------------
    # Clean spaces
    # --------------------------------------------

    q = re.sub(
        r"\s+",
        " ",
        q
    ).strip()

    return q


# ============================================================
# 13. EXACT PROJECT ID SEARCH
# ============================================================

def exact_project_id_search(question):

    q = normalize_text(
        question
    )

    patterns = [

        r"\bproject\s+id\s*[:#-]?\s*(\d+)\b",

        r"\bproject\s+number\s*[:#-]?\s*(\d+)\b",

        r"\bproject\s+(\d+)\b",

        r"\bid\s*[:#-]?\s*(\d+)\b"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            q
        )

        if not match:
            continue

        project_id = match.group(1)

        matches = gian_df[
            gian_df["id"].str.strip()
            == project_id
        ]

        results = []

        for _, row in matches.iterrows():

            results.append(
                make_result(
                    row,
                    score=5.0,
                    reason="exact project ID"
                )
            )

        return results

    return []


# ============================================================
# 14. EXACT PROJECT NAME SEARCH
# ============================================================

def exact_project_name_search(question):

    project_name = extract_project_name(
        question
    )

    if not project_name:
        return []

    matches = gian_df[
        gian_df["project_name_norm"]
        == project_name
    ]

    results = []

    for _, row in matches.iterrows():

        results.append(
            make_result(
                row,
                score=5.0,
                reason="exact project name"
            )
        )

    return results


# ============================================================
# 15. PARTICIPANT NAME EXTRACTION
# ============================================================

def extract_person_name(question):

    """
    Extract the likely person name from queries such as:

    Which project is associated with
    Belgi Akanksha Manoj?

    Which project belongs to
    Vinayak Yeshwant?
    """

    q = normalize_text(
        question
    )

    patterns = [

        r"which project is associated with\s+(.+)$",

        r"which project is related to\s+(.+)$",

        r"which project is connected to\s+(.+)$",

        r"which project belongs to\s+(.+)$",

        r"project associated with\s+(.+)$",

        r"project related to\s+(.+)$",

        r"project connected to\s+(.+)$"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            q
        )

        if match:

            name = match.group(1)

            name = re.sub(
                r"[?.!]+$",
                "",
                name
            )

            return name.strip()

    return ""


# ============================================================
# 16. PARTICIPANT SEARCH
# ============================================================

def participant_search(question):

    person_name = extract_person_name(
        question
    )

    if not person_name:

        return []

    person_norm = normalize_text(
        person_name
    )

    if not person_norm:

        return []

    results = []

    for _, row in gian_df.iterrows():

        participants = row[
            "participants_norm"
        ]

        if not participants:

            continue

        # ----------------------------------------
        # Full participant name inside field
        # ----------------------------------------

        if person_norm in participants:

            results.append(
                make_result(
                    row,
                    score=5.0,
                    reason="participant entity match"
                )
            )

    return results


# ============================================================
# 17. COLLEGE LOCATIONS
# ============================================================

KNOWN_LOCATIONS = {

    "miraj",
    "mumbai",
    "yavatmal",
    "nashik",
    "nasik",
    "nanded",
    "dhule",
    "jalana",
    "jalna",
    "washim",
    "arvi",
    "ahmednagar",
    "ahmednager",
    "sangamner",
    "bramhapuri",
    "nandad",
    "nagpur",
    "pune",
    "solapur",
    "kolhapur",
    "satara",
    "amravati",
    "akola",
    "wardha",
    "ratnagiri",
    "thane",
    "aurangabad",
    "chandrapur"
}


# ============================================================
# 18. EXTRACT COLLEGE LOCATION
# ============================================================

def extract_college_location(question):

    q = normalize_text(
        question
    )

    words = set(
        q.split()
    )

    found = []

    for location in KNOWN_LOCATIONS:

        if location in words:

            found.append(
                location
            )

    return found


# ============================================================
# 19. COLLEGE SEARCH
# ============================================================

def exact_college_search(question):

    locations = extract_college_location(
        question
    )

    if not locations:

        return []

    results = []

    for _, row in gian_df.iterrows():

        college = row[
            "college_norm"
        ]

        if not college:
            continue

        for location in locations:

            if re.search(
                r"\b"
                + re.escape(location)
                + r"\b",
                college
            ):

                results.append(
                    make_result(
                        row,
                        score=4.0,
                        reason=(
                            "exact college/location match"
                        )
                    )
                )

                break

    return results


# ============================================================
# 20. QUESTION TYPE DETECTION
# ============================================================

def is_participant_question(question):

    q = normalize_text(
        question
    )

    return (
        "participant" in q
        or "participants" in q
    )


def is_college_question(question):

    q = normalize_text(
        question
    )

    return (
        "college" in q
        or "polytechnic" in q
        or "institute" in q
    )


# ============================================================
# 21. MAKE RESULT
# ============================================================

def make_result(
    row,
    score=0.0,
    reason=""
):

    return {

        "record_id":
            row.get(
                "record_id",
                ""
            ),

        "project_id":
            row.get(
                "id",
                ""
            ),

        "project_name":
            row.get(
                "project_name",
                ""
            ),

        "participants":
            row.get(
                "participants",
                ""
            ),

        "abstract":
            row.get(
                "abstract",
                ""
            ),

        "college":
            row.get(
                "college_status",
                ""
            ),

        "source":
            row.get(
                "source",
                GIAN_SOURCE
            ),

        "source_url":
            row.get(
                "source_url",
                GIAN_URL
            ),

        "data_category":
            row.get(
                "data_category",
                "GIAN Nidhi Project"
            ),

        "score":
            score,

        "reasons":
            [reason]
            if reason
            else []
    }


# ============================================================
# 22. SEMANTIC SEARCH
# ============================================================

def semantic_search(
    question,
    top_k=10
):

    try:

        query_embedding = (
            embedding_model
            .encode(
                question
            )
            .tolist()
        )

        results = collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=top_k,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

    except Exception as e:

        print(
            f"\nSemantic search error: {e}"
        )

        return []

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    output = []

    for i in range(
        len(documents)
    ):

        metadata = (
            metadatas[i]
            if i < len(metadatas)
            else {}
        )

        distance = (
            distances[i]
            if i < len(distances)
            else 999
        )

        score = (
            1 / (1 + distance)
        )

        output.append({

            "record_id":
                metadata.get(
                    "record_id",
                    ""
                ),

            "project_id":
                metadata.get(
                    "project_id",
                    ""
                ),

            "project_name":
                metadata.get(
                    "project_name",
                    ""
                ),

            "participants":
                metadata.get(
                    "participants",
                    ""
                ),

            "abstract":
                metadata.get(
                    "abstract",
                    ""
                ),

            "college":
                metadata.get(
                    "college",
                    ""
                ),

            "source":
                metadata.get(
                    "source",
                    GIAN_SOURCE
                ),

            "source_url":
                metadata.get(
                    "source_url",
                    GIAN_URL
                ),

            "data_category":
                metadata.get(
                    "data_category",
                    "GIAN Nidhi Project"
                ),

            "score":
                score,

            "reasons":
                ["semantic similarity"]
        })

    return output


# ============================================================
# 23. REMOVE DUPLICATES
# ============================================================

def remove_duplicate_results(
    results
):

    unique = {}

    for result in results:

        project_id = result.get(
            "project_id",
            ""
        )

        if not project_id:
            continue

        if project_id not in unique:

            unique[
                project_id
            ] = result

        else:

            if (
                result["score"]
                >
                unique[
                    project_id
                ]["score"]
            ):

                unique[
                    project_id
                ] = result

    return list(
        unique.values()
    )


# ============================================================
# 24. HYBRID SEARCH
# ============================================================

def hybrid_search(
    question,
    top_k=5
):

    print("\n" + "=" * 70)

    print(
        f"QUESTION:\n{question}"
    )

    print("=" * 70)


    # ========================================================
    # A. EXACT PROJECT ID
    # ========================================================

    results = exact_project_id_search(
        question
    )

    if results:

        print(
            "\nSearch type: EXACT PROJECT ID"
        )

        return results


    # ========================================================
    # B. PROJECT -> PARTICIPANTS
    # ========================================================

    if is_participant_question(
        question
    ):

        project_results = (
            exact_project_name_search(
                question
            )
        )

        if project_results:

            print(
                "\nSearch type: "
                "PROJECT -> PARTICIPANTS"
            )

            for result in project_results:

                result["reasons"] = [
                    "exact project name"
                ]

            return project_results


    # ========================================================
    # C. EXACT PROJECT NAME
    # ========================================================

    results = exact_project_name_search(
        question
    )

    if results:

        print(
            "\nSearch type: EXACT PROJECT NAME"
        )

        return results


    # ========================================================
    # D. PARTICIPANT -> PROJECT
    # ========================================================

    participant_results = (
        participant_search(
            question
        )
    )

    if participant_results:

        print(
            "\nSearch type: "
            "PARTICIPANT -> PROJECT"
        )

        return participant_results


    # ========================================================
    # E. COLLEGE
    # ========================================================

    college_results = (
        exact_college_search(
            question
        )
    )

    if college_results:

        print(
            "\nSearch type: COLLEGE / LOCATION"
        )

        return college_results


    # ========================================================
    # F. SEMANTIC FALLBACK
    # ========================================================

    print(
        "\nSearch type: SEMANTIC SEARCH"
    )

    results = semantic_search(
        question,
        top_k=10
    )

    return results[:top_k]


# ============================================================
# 25. PRINT RESULTS
# ============================================================

def print_results(
    results
):

    results = remove_duplicate_results(
        results
    )

    print(
        f"\nTotal matching records: "
        f"{len(results)}"
    )

    print("-" * 70)

    if not results:

        print(
            "\nThe available sources do not "
            "provide sufficient information "
            "to answer this."
        )

        return


    for index, result in enumerate(
        results,
        start=1
    ):

        print(
            f"\nRESULT {index}"
        )

        print(
            f"Project ID   : "
            f"{result.get('project_id', '')}"
        )

        print(
            f"Project Name : "
            f"{result.get('project_name', '')}"
        )

        print(
            f"Participants : "
            f"{result.get('participants', '')}"
        )

        print(
            f"College      : "
            f"{result.get('college', '')}"
        )

        print(
            f"Abstract     : "
            f"{result.get('abstract', '')}"
        )

        print(
            f"Source       : "
            f"{result.get('source', '')}"
        )

        print(
            f"Source URL   : "
            f"{result.get('source_url', '')}"
        )

        print(
            f"Data Category: "
            f"{result.get('data_category', '')}"
        )

        print(
            f"Score        : "
            f"{result.get('score', 0):.4f}"
        )

        print(
            f"Reasons      : "
            f"{result.get('reasons', [])}"
        )

        print("-" * 70)


# ============================================================
# 26. TEST QUESTIONS
# ============================================================

TEST_QUESTIONS = [

    # --------------------------------------------
    # Project ID
    # --------------------------------------------

    "What is project ID 640?",

    "What is project ID 639?",


    # --------------------------------------------
    # Project name
    # --------------------------------------------

    "What is the 360 Metallurgy Flexible Drilling Machine project?",

    "What is Continuous Variable Transmission?",


    # --------------------------------------------
    # Project -> participant
    # --------------------------------------------

    "Who are the participants of Continuous Variable Transmission?",


    # --------------------------------------------
    # Participant -> project
    # --------------------------------------------

    "Which project is associated with Belgi Akanksha Manoj?",


    # --------------------------------------------
    # College
    # --------------------------------------------

    "Which projects are associated with Government Polytechnic Miraj?",


    # --------------------------------------------
    # Project ID -> college
    # --------------------------------------------

    "Which college is associated with project ID 4?"
]


# ============================================================
# 27. RUN TESTS
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 70)
    print("GIAN NIDHI HYBRID QUERY SYSTEM")
    print("=" * 70)

    print(
        f"\nCSV records      : "
        f"{len(gian_df)}"
    )

    print(
        f"ChromaDB records : "
        f"{collection.count()}"
    )

    print(
        f"Embedding model  : "
        f"{MODEL_NAME}"
    )

    print(
        f"Source URL       : "
        f"{GIAN_URL}"
    )

    print(
        "\nRunning test queries..."
    )


    for question in TEST_QUESTIONS:

        results = hybrid_search(
            question
        )

        print_results(
            results
        )

        print("\n")


    print("=" * 70)
    print("ALL TEST QUERIES COMPLETED")
    print("=" * 70)