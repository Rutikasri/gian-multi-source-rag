# ============================================================
# GIAN MULTI-SOURCE RAG SYSTEM
# ============================================================
#
# Sources:
#   1. 51st Shodhyatra
#   2. 53rd Shodhyatra
#   3. Shodhyatra relationship records
#   4. GIAN Nidhi
#
# Vector DB:
#   ChromaDB
#
# Embedding model:
#   sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
#
# LLM:
#   Groq - openai/gpt-oss-20b
#
# ============================================================


# ============================================================
# 1. IMPORTS
# ============================================================

import os
import re
import pandas as pd
import chromadb

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from groq import Groq


# ============================================================
# 2. PATHS / CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CHROMA_PATH = os.path.join(
    BASE_DIR,
    "chroma_db"
)

COLLECTION_NAME = "gian_knowledge"

GIAN_CSV = os.path.join(
    BASE_DIR,
    "data",
    "gian_nidhi.csv"
)

EMBEDDING_MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

LLM_MODEL = "openai/gpt-oss-20b"

GIAN_NIDHI_URL = (
    "https://gian.org/gian-nidhi/"
)


# ============================================================
# 3. STARTUP
# ============================================================

print("=" * 70)
print("INITIALIZING GIAN MULTI-SOURCE RAG")
print("=" * 70)


# ============================================================
# 4. LOAD ENVIRONMENT
# ============================================================

load_dotenv()

api_key = os.getenv(
    "GROQ_API_KEY"
)

if not api_key:
    raise ValueError(
        "\nGROQ_API_KEY was not found.\n"
        "Please check your .env file.\n"
    )


# ============================================================
# 5. LOAD GROQ
# ============================================================

print("\nInitializing Groq...")

groq_client = Groq(
    api_key=api_key
)

print("Groq client initialized.")


# ============================================================
# 6. LOAD GIAN NIDHI CSV
# ============================================================

print("\nLoading GIAN Nidhi data...")

if not os.path.exists(GIAN_CSV):

    raise FileNotFoundError(
        f"\nGIAN Nidhi CSV not found:\n{GIAN_CSV}"
    )


gian_df = pd.read_csv(
    GIAN_CSV,
    dtype=str
).fillna("")


print(
    f"GIAN Nidhi records loaded: "
    f"{len(gian_df)}"
)


# ============================================================
# 7. LOAD CHROMADB
# ============================================================

print("\nLoading ChromaDB...")

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
    f"Collection records: "
    f"{collection.count()}"
)


# ============================================================
# 8. LOAD EMBEDDING MODEL
# ============================================================

print("\nLoading embedding model...")

print(
    f"Model: {EMBEDDING_MODEL_NAME}"
)

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL_NAME
)

print("Embedding model loaded.")


# ============================================================
# 9. SOURCE KEYWORDS
# ============================================================
#
# These are retrieval signals, NOT fabricated facts.
# They help identify which source family a question refers to.
# ============================================================

SHODHYATRA_KEYWORDS = [

    "shodhyatra",
    "shodh yatra",

    "khejri",
    "thornless",

    "paryavaran van",

    "sunda ram",
    "sundaram",

    "rameshwar lal",
    "rameshwar prasad",

    "rawalchand",
    "rahulchand",

    "bhambhu",

    "carrot variety",
    "sweet potato",

    "camel farming",

    "traditional healer",
    "healers",

    "bonsai",

    "archery training",

    "bhili dolls",
    "tribal dolls",

    "adivasi gudiya",

    "pithora",
    "pithora art",

    "gatha smriti",
    "memory pillars",

    "mahua",
    "seed-breaking machine",

    "welding machine",

    "soldier physical academy",

    "banana fiber",

    "banana-fiber",

    "native seeds",

    "jeevamrit",

    "vermicompost",

    "natural farming",

    "bhavai",

    "rathwa",

    "bhil artist",

    "tribal toys",

    "tribal art"
]


GIAN_KEYWORDS = [

    "gian nidhi",

    "project id",

    "project number",

    "sr no",

    "serial number",

    "college",

    "polytechnic",

    "participants",

    "participant",

    "abstract"
]


# ============================================================
# 10. NORMALIZATION
# ============================================================

def normalize_text(text):

    text = str(text).lower()

    text = text.replace(
        "–",
        "-"
    )

    text = text.replace(
        "—",
        "-"
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# 11. DETECT SOURCE TYPE
# ============================================================

def detect_source_type(question):

    q = normalize_text(
        question
    )

    shodhyatra_matches = 0
    gian_matches = 0


    for keyword in SHODHYATRA_KEYWORDS:

        if keyword in q:

            shodhyatra_matches += 1


    for keyword in GIAN_KEYWORDS:

        if keyword in q:

            gian_matches += 1


    if (
        shodhyatra_matches > 0
        and
        gian_matches == 0
    ):

        return "shodhyatra"


    if (
        gian_matches > 0
        and
        shodhyatra_matches == 0
    ):

        return "gian"


    if (
        shodhyatra_matches > 0
        and
        gian_matches > 0
    ):

        return "multi"


    return "unknown"


# ============================================================
# 12. DETECT RELATIONSHIP QUESTIONS
# ============================================================

def is_relationship_question(question):

    q = normalize_text(
        question
    )

    relationship_terms = [

        "who developed",
        "who invented",
        "who created",
        "who built",
        "who made",

        "developed by",
        "invented by",
        "created by",
        "built by",
        "made by",

        "who is associated with",
        "associated with",

        "who practices",
        "practices",

        "who founded",
        "founded by"
    ]


    for term in relationship_terms:

        if term in q:

            return True


    return False


# ============================================================
# 13. CHROMADB SEMANTIC SEARCH
# ============================================================

def chroma_search(
    question,
    n_results=20
):

    query_embedding = (
        embedding_model
        .encode(
            [question],
            normalize_embeddings=True
        )
        .tolist()
    )


    results = collection.query(

        query_embeddings=
            query_embedding,

        n_results=
            n_results,

        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )


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


        score = 1 / (
            1 + float(distance)
        )


        output.append({

            "document":
                documents[i],

            "metadata":
                metadata,

            "semantic_score":
                score,

            "final_score":
                score
        })


    return output


# ============================================================
# 14. CALCULATE SOURCE BOOST
# ============================================================

def source_boost(
    question,
    metadata,
    document
):

    source_type = detect_source_type(
        question
    )

    source = normalize_text(
        metadata.get(
            "source",
            ""
        )
    )

    record_kind = normalize_text(
        metadata.get(
            "record_kind",
            ""
        )
    )

    document_lower = normalize_text(
        document
    )


    boost = 0.0


    # --------------------------------------------------------
    # Shodhyatra query
    # --------------------------------------------------------

    if source_type == "shodhyatra":

        if "shodhyatra" in source:

            boost += 2.0


        if record_kind == "entity":

            boost += 0.5


        if record_kind == "relationship":

            boost += 1.5


        # Match specific Shodhyatra terms
        for keyword in SHODHYATRA_KEYWORDS:

            if keyword in normalize_text(question):

                if keyword in document_lower:

                    boost += 1.0


    # --------------------------------------------------------
    # GIAN query
    # --------------------------------------------------------

    elif source_type == "gian":

        if "gian nidhi" in source:

            boost += 2.0


        if record_kind == "gian_nidhi":

            boost += 1.0


    # --------------------------------------------------------
    # Multi-source query
    # --------------------------------------------------------

    elif source_type == "multi":

        # No strong source exclusion.
        # Both source families remain eligible.

        boost += 0.5


    return boost


# ============================================================
# 15. ENTITY / RELATIONSHIP BOOST
# ============================================================

def entity_relationship_boost(
    question,
    result
):

    metadata = result.get(
        "metadata",
        {}
    )

    document = result.get(
        "document",
        ""
    )


    q = normalize_text(
        question
    )

    doc = normalize_text(
        document
    )


    boost = 0.0


    # --------------------------------------------------------
    # Relationship records
    # --------------------------------------------------------

    record_kind = normalize_text(
        metadata.get(
            "record_kind",
            ""
        )
    )


    relationship_type = normalize_text(
        metadata.get(
            "relationship_type",
            ""
        )
    )


    if is_relationship_question(
        question
    ):

        if record_kind == "relationship":

            boost += 3.0


        relationship_words = [

            "developed",
            "created",
            "founded",
            "practices",
            "invented",
            "built"
        ]


        for word in relationship_words:

            if word in q:

                if word in relationship_type:

                    boost += 2.0


                elif word in doc:

                    boost += 0.5


    # --------------------------------------------------------
    # Important phrase matching
    # --------------------------------------------------------

    important_phrases = [

        "thornless khejri",

        "khejri",

        "bhili dolls",

        "adivasi gudiya",

        "pithora art",

        "mahua seed-breaking machine",

        "hand-operated mahua",

        "welding machine",

        "soldier physical academy",

        "banana fiber",

        "gatha smriti"
    ]


    for phrase in important_phrases:

        if phrase in q:

            if phrase in doc:

                boost += 3.0


    return boost


# ============================================================
# 16. RERANK SEMANTIC RESULTS
# ============================================================

def rerank_results(
    question,
    results
):

    for result in results:

        metadata = result.get(
            "metadata",
            {}
        )

        document = result.get(
            "document",
            ""
        )


        result["final_score"] = (

            result.get(
                "semantic_score",
                0
            )

            +

            source_boost(
                question,
                metadata,
                document
            )

            +

            entity_relationship_boost(
                question,
                result
            )
        )


    results.sort(
        key=lambda x:
            x["final_score"],
        reverse=True
    )


    return results


# ============================================================
# 17. STRUCTURED GIAN SEARCH
# ============================================================

def structured_gian_search(
    question
):

    q = normalize_text(
        question
    )


    matches = []


    # ========================================================
    # PROJECT ID
    # ========================================================

    id_match = re.search(
        r"\b(?:project\s*)?"
        r"(?:id|number|no\.?)\s*"
        r"(\d{1,4})\b",
        q
    )


    if id_match:

        project_id = (
            id_match.group(1)
        )


        rows = gian_df[
            gian_df["id"]
            .astype(str)
            .str.strip()
            .eq(project_id)
        ]


        if len(rows) > 0:

            print(
                "\nSearch type: EXACT PROJECT ID"
            )


            for _, row in rows.iterrows():

                matches.append(
                    create_gian_result(
                        row,
                        score=10.0,
                        reason="exact project ID"
                    )
                )


            return matches


    # ========================================================
    # PROJECT NAME
    # ========================================================

    project_columns = [
        "project_name"
    ]


    for _, row in gian_df.iterrows():

        project_name = normalize_text(
            row.get(
                "project_name",
                ""
            )
        )


        if not project_name:

            continue


        # Exact project title
        if project_name == q:

            matches.append(
                create_gian_result(
                    row,
                    score=9.0,
                    reason="exact project name"
                )
            )

            continue


        # Question contains project title
        if (
            len(project_name) >= 8
            and
            project_name in q
        ):

            matches.append(
                create_gian_result(
                    row,
                    score=8.0,
                    reason="project name in question"
                )
            )


    if matches:

        print(
            "\nSearch type: PROJECT NAME"
        )

        return matches


    # ========================================================
    # PARTICIPANT
    # ========================================================

    if (
        "participant" in q
        or
        "who is associated" in q
    ):

        for _, row in gian_df.iterrows():

            participants = normalize_text(
                row.get(
                    "participants",
                    ""
                )
            )


            if not participants:

                continue


            participant_list = [
                normalize_text(
                    x
                )
                for x in participants.split(",")
            ]


            for participant in participant_list:

                if (
                    participant
                    and
                    participant in q
                ):

                    matches.append(
                        create_gian_result(
                            row,
                            score=9.0,
                            reason=(
                                "participant -> project"
                            )
                        )
                    )

                    break


        if matches:

            print(
                "\nSearch type: PARTICIPANT -> PROJECT"
            )

            return matches


    # ========================================================
    # COLLEGE
    # ========================================================

    college_terms = [

        "government polytechnic",
        "govt. polytechnic",
        "polytechnic",
        "college"
    ]


    if any(
        term in q
        for term in college_terms
    ):

        # Extract meaningful location after
        # Government Polytechnic / Polytechnic
        location_words = [

            "miraj",
            "mumbai",
            "bramhapuri",
            "yavatmal",
            "nanded",
            "dhule",
            "nashik",
            "nasik",
            "jalana",
            "washim",
            "kopargaon",
            "arvi",
            "ahmednager",
            "sangamner"
        ]


        requested_location = None


        for location in location_words:

            if location in q:

                requested_location = location
                break


        if requested_location:

            for _, row in gian_df.iterrows():

                college = normalize_text(
                    row.get(
                        "college_status",
                        ""
                    )
                )


                if (
                    requested_location
                    in college
                ):

                    matches.append(
                        create_gian_result(
                            row,
                            score=7.0,
                            reason=(
                                "college/location match"
                            )
                        )
                    )


            if matches:

                print(
                    "\nSearch type: COLLEGE / LOCATION"
                )

                return matches


    return []


# ============================================================
# 18. CREATE GIAN RESULT
# ============================================================

def create_gian_result(
    row,
    score,
    reason
):

    project_id = str(
        row.get(
            "id",
            ""
        )
    ).strip()


    record_id = str(
        row.get(
            "record_id",
            ""
        )
    ).strip()


    project_name = str(
        row.get(
            "project_name",
            ""
        )
    ).strip()


    participants = str(
        row.get(
            "participants",
            ""
        )
    ).strip()


    abstract = str(
        row.get(
            "abstract",
            ""
        )
    ).strip()


    college = str(
        row.get(
            "college_status",
            ""
        )
    ).strip()


    document = f"""
GIAN Nidhi project: {project_name}.
Project ID: {project_id}.
Record ID: {record_id}.
Participants: {participants}.
Abstract: {abstract}.
College: {college}.
Source: GIAN Nidhi.
Source URL: {GIAN_NIDHI_URL}.
""".strip()


    metadata = {

        "record_id":
            record_id,

        "project_id":
            project_id,

        "project_name":
            project_name,

        "participants":
            participants,

        "college":
            college,

        "source":
            "GIAN Nidhi",

        "source_url":
            GIAN_NIDHI_URL,

        "document_title":
            "GIAN Nidhi",

        "page":
            "",

        "data_category":
            "GIAN Nidhi Project",

        "record_kind":
            "gian_nidhi",

        "confidence":
            "source"
    }


    return {

        "document":
            document,

        "metadata":
            metadata,

        "semantic_score":
            0.0,

        "final_score":
            score,

        "retrieval_reason":
            reason
    }


# ============================================================
# 19. REMOVE DUPLICATES
# ============================================================

def remove_duplicates(
    results
):

    unique = {}


    for result in results:

        metadata = result.get(
            "metadata",
            {}
        )


        record_id = str(
            metadata.get(
                "record_id",
                ""
            )
        ).strip()


        project_id = str(
            metadata.get(
                "project_id",
                ""
            )
        ).strip()


        source = str(
            metadata.get(
                "source",
                ""
            )
        ).strip()


        if record_id:

            key = (
                "record",
                record_id
            )

        elif project_id:

            key = (
                "project",
                project_id,
                source
            )

        else:

            key = (
                "document",
                source,
                result.get(
                    "document",
                    ""
                )
            )


        if key not in unique:

            unique[key] = result

        else:

            if (
                result.get(
                    "final_score",
                    0
                )
                >
                unique[key].get(
                    "final_score",
                    0
                )
            ):

                unique[key] = result


    return list(
        unique.values()
    )


# ============================================================
# 20. FINAL RETRIEVAL FUNCTION
# ============================================================

def retrieve(
    question,
    n_results=5
):

    # ========================================================
    # STEP 1
    # Try structured GIAN retrieval
    # ========================================================

    structured_results = (
        structured_gian_search(
            question
        )
    )


    if structured_results:

        return (
            remove_duplicates(
                structured_results
            )[:n_results]
        )


    # ========================================================
    # STEP 2
    # Semantic search across all 703 records
    # ========================================================

    print(
        "\nSearch type: SEMANTIC SEARCH"
    )


    results = chroma_search(
        question,
        n_results=25
    )


    # ========================================================
    # STEP 3
    # Source-aware reranking
    # ========================================================

    results = rerank_results(
        question,
        results
    )


    results = remove_duplicates(
        results
    )


    # ========================================================
    # STEP 4
    # IMPORTANT:
    #
    # If this is clearly a Shodhyatra question, keep
    # Shodhyatra results above unrelated GIAN records.
    # ========================================================

    source_type = detect_source_type(
        question
    )


    if source_type == "shodhyatra":

        shodhyatra_results = [

            r

            for r in results

            if "shodhyatra"
            in normalize_text(
                r["metadata"].get(
                    "source",
                    ""
                )
            )
        ]


        if shodhyatra_results:

            results = (
                shodhyatra_results
                +
                [
                    r
                    for r in results
                    if r not in shodhyatra_results
                ]
            )


    # ========================================================
    # STEP 5
    # Return top results
    # ========================================================

    return results[
        :n_results
    ]


# ============================================================
# 21. BUILD CONTEXT FOR LLM
# ============================================================

def build_context(
    results
):

    if not results:

        return ""


    context_parts = []


    for index, result in enumerate(
        results,
        start=1
    ):

        metadata = result.get(
            "metadata",
            {}
        )


        source = metadata.get(
            "source",
            ""
        )


        source_url = metadata.get(
            "source_url",
            ""
        )


        document_title = metadata.get(
            "document_title",
            ""
        )


        page = metadata.get(
            "page",
            ""
        )


        record_id = metadata.get(
            "record_id",
            ""
        )


        project_id = metadata.get(
            "project_id",
            ""
        )


        project_name = metadata.get(
            "project_name",
            ""
        )


        participants = metadata.get(
            "participants",
            ""
        )


        college = metadata.get(
            "college",
            ""
        )


        author = metadata.get(
            "author",
            ""
        )


        innovator = metadata.get(
            "innovator_name",
            ""
        )


        innovation = metadata.get(
            "innovation_name",
            ""
        )


        publication = metadata.get(
            "publication_name",
            ""
        )


        publication_year = metadata.get(
            "publication_year",
            ""
        )


        data_category = metadata.get(
            "data_category",
            ""
        )


        organisation = metadata.get(
            "organisation",
            metadata.get(
                "relevant_organisation",
                ""
            )
        )


        relationship_type = metadata.get(
            "relationship_type",
            ""
        )


        context = f"""
============================================================
EVIDENCE {index}
============================================================

Source:
{source or "Not available"}

Source URL:
{source_url or "Not available"}

Document Title:
{document_title or "Not available"}

Page:
{page or "Not available"}

Record ID:
{record_id or "Not available"}

Project ID:
{project_id or "Not available"}

Project Name:
{project_name or "Not available"}

Participants:
{participants or "Not available"}

College:
{college or "Not available"}

Author:
{author or "Not available"}

Innovator Name:
{innovator or "Not available"}

Innovation Name:
{innovation or "Not available"}

Publication Name:
{publication or "Not available"}

Publication Year:
{publication_year or "Not available"}

Organisation:
{organisation or "Not available"}

Relationship Type:
{relationship_type or "Not available"}

Data Category:
{data_category or "Not available"}

Evidence Text:
{result.get("document", "")}

============================================================
""".strip()


        context_parts.append(
            context
        )


    return "\n\n".join(
        context_parts
    )


# ============================================================
# 22. SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are a source-grounded knowledge-base assistant.

Your knowledge base contains:

1. 51st Shodhyatra
2. 53rd Shodhyatra
3. Shodhyatra relationship records
4. GIAN Nidhi

You MUST answer using ONLY the retrieved evidence.

============================================================
STRICT GROUNDING RULES
============================================================

1. Never use outside knowledge.

2. Never fabricate information.

3. Never invent:

- names
- innovators
- participants
- authors
- innovation names
- project names
- awards
- dates
- locations
- organisations
- colleges
- publications
- technical details
- relationships
- sources
- page numbers

4. Similar names do NOT establish a relationship.

5. Similar project titles do NOT establish a relationship.

6. Similar locations do NOT establish a relationship.

7. Only report relationships explicitly supported by evidence.

8. GIAN Nidhi "participants" must remain participants.

Do NOT automatically call a participant:

- innovator
- inventor
- author
- developer
- creator

unless the evidence explicitly supports that terminology.

9. Do not treat an idea, competition entry, traditional
practice, historical person, or organisation as an innovator
unless the evidence explicitly identifies them that way.

10. Do not combine information from two unrelated records.

11. If multiple sources are relevant, separate them clearly.

12. Preserve the terminology of the source.

13. If information is missing, do not guess.

============================================================
INSUFFICIENT INFORMATION
============================================================

If the retrieved evidence is not sufficient to answer the
question, respond EXACTLY:

"The available sources do not provide sufficient information
to answer this."

Do not add a guessed answer after this statement.

============================================================
SOURCE ATTRIBUTION
============================================================

Every factual answer must include:

Source:
Page / Record:
Source URL:

For GIAN Nidhi, use the supplied GIAN Nidhi URL.

For Shodhyatra records, use the supplied Shodhyatra URL.

============================================================
ANSWER FORMAT
============================================================

Answer:
<direct answer>

Relevant Information:
- Innovator / Participant / Person:
- Innovation / Project:
- Author:
- Organisation / College:
- Source:
- Page / Record:
- Source URL:

Only include fields supported by evidence.

For multiple sources, use:

Source 1:
...

Source 2:
...

Do not merge unsupported relationships.
"""


# ============================================================
# 23. GENERATE ANSWER
# ============================================================

def generate_answer(
    question,
    context
):

    if not context:

        return (
            "The available sources do not provide sufficient "
            "information to answer this."
        )


    user_prompt = f"""
QUESTION:

{question}


RETRIEVED EVIDENCE:

{context}


TASK:

Answer the question using ONLY the retrieved evidence.

Do not use outside knowledge.

Do not infer unsupported relationships.

Do not fabricate missing information.

Provide source attribution.

Include page or record information when available.

If the evidence is insufficient, respond exactly:

"The available sources do not provide sufficient information
to answer this."
"""


    try:

        response = (
            groq_client
            .chat
            .completions
            .create(

                model=LLM_MODEL,

                temperature=0,

                max_tokens=700,

                messages=[

                    {
                        "role":
                            "system",

                        "content":
                            SYSTEM_PROMPT
                    },

                    {
                        "role":
                            "user",

                        "content":
                            user_prompt
                    }
                ]
            )
        )


        answer = (
            response
            .choices[0]
            .message
            .content
        )


        if not answer:

            return (
                "The available sources do not provide "
                "sufficient information to answer this."
            )


        return answer.strip()


    except Exception as e:

        print(
            "\nGroq generation error:"
        )

        print(e)


        return (
            "The RAG system could not generate an answer."
        )


# ============================================================
# 24. DISPLAY RETRIEVED EVIDENCE
# ============================================================

def display_evidence(
    results
):

    for index, result in enumerate(
        results,
        start=1
    ):

        metadata = result.get(
            "metadata",
            {}
        )


        print(
            f"\nEvidence {index}"
        )

        print(
            "-" * 60
        )


        print(
            "Source       : "
            + str(
                metadata.get(
                    "source",
                    "N/A"
                )
            )
        )


        print(
            "Document     : "
            + str(
                metadata.get(
                    "document_title",
                    ""
                )
                or "N/A"
            )
        )


        print(
            "Page         : "
            + str(
                metadata.get(
                    "page",
                    ""
                )
                or "N/A"
            )
        )


        print(
            "Record ID    : "
            + str(
                metadata.get(
                    "record_id",
                    ""
                )
                or "N/A"
            )
        )


        print(
            "Project ID   : "
            + str(
                metadata.get(
                    "project_id",
                    ""
                )
                or "N/A"
            )
        )


        print(
            "Data Category: "
            + str(
                metadata.get(
                    "data_category",
                    ""
                )
                or "N/A"
            )
        )


        print(
            "Score        : "
            + f"{result.get('final_score', 0):.4f}"
        )


# ============================================================
# 25. COMPLETE QUESTION PIPELINE
# ============================================================

def answer_question(
    question
):

    question = question.strip()


    if not question:

        print(
            "\nPlease enter a question."
        )

        return


    print("\n")
    print("=" * 80)
    print("GIAN MULTI-SOURCE RAG")
    print("=" * 80)


    print(
        f"\nQuestion:\n{question}"
    )


    # --------------------------------------------------------
    # Retrieval
    # --------------------------------------------------------

    results = retrieve(
        question,
        n_results=5
    )


    print(
        f"\nRetrieved evidence: "
        f"{len(results)}"
    )


    if not results:

        print(
            "\nNo evidence retrieved."
        )


        answer = (
            "The available sources do not provide "
            "sufficient information to answer this."
        )


        print("\n")
        print("=" * 80)
        print("ANSWER")
        print("=" * 80)
        print("\n" + answer)

        return answer


    # --------------------------------------------------------
    # Display evidence summary
    # --------------------------------------------------------

    display_evidence(
        results
    )


    # --------------------------------------------------------
    # Build context
    # --------------------------------------------------------

    context = build_context(
        results
    )


    # --------------------------------------------------------
    # Generate answer
    # --------------------------------------------------------

    print(
        "\nGenerating answer..."
    )


    answer = generate_answer(
        question,
        context
    )


    # --------------------------------------------------------
    # Display answer
    # --------------------------------------------------------

    print("\n")
    print("=" * 80)
    print("ANSWER")
    print("=" * 80)


    print(
        "\n" + answer
    )


    # --------------------------------------------------------
    # Display evidence
    # --------------------------------------------------------

    print("\n")
    print("=" * 80)
    print("RETRIEVED EVIDENCE")
    print("=" * 80)


    for index, result in enumerate(
        results,
        start=1
    ):

        metadata = result.get(
            "metadata",
            {}
        )


        print(
            f"\nEvidence {index}"
        )

        print(
            "-" * 80
        )


        print(
            result.get(
                "document",
                ""
            )
        )


        print(
            "\nSource: "
            +
            str(
                metadata.get(
                    "source",
                    "Not available"
                )
            )
        )


        print(
            "Page: "
            +
            str(
                metadata.get(
                    "page",
                    ""
                )
                or "Not available"
            )
        )


        print(
            "Record ID: "
            +
            str(
                metadata.get(
                    "record_id",
                    ""
                )
                or "Not available"
            )
        )


        print(
            "Source URL: "
            +
            str(
                metadata.get(
                    "source_url",
                    ""
                )
                or "Not available"
            )
        )


    return answer


# ============================================================
# 26. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 80)
    print("GIAN MULTI-SOURCE RAG SYSTEM")
    print("=" * 80)


    print(
        "\nLLM Model:"
    )

    print(
        LLM_MODEL
    )


    print(
        "\nEmbedding Model:"
    )

    print(
        EMBEDDING_MODEL_NAME
    )


    print(
        "\nVector Database:"
    )

    print(
        "ChromaDB"
    )


    print(
        "\nKnowledge Base Records:"
    )

    print(
        collection.count()
    )


    print(
        "\nKnowledge Sources:"
    )

    print(
        "1. 51st Shodhyatra"
    )

    print(
        "2. 53rd Shodhyatra"
    )

    print(
        "3. Shodhyatra relationship records"
    )

    print(
        "4. GIAN Nidhi"
    )


    print(
        "\nType 'exit' or 'quit' to stop."
    )


    while True:

        try:

            question = input(
                "\nAsk a question: "
            ).strip()


        except (
            KeyboardInterrupt,
            EOFError
        ):

            print(
                "\nExiting..."
            )

            break


        if question.lower() in {
            "exit",
            "quit"
        }:

            print(
                "\nExiting..."
            )

            break


        if not question:

            print(
                "Please enter a question."
            )

            continue


        try:

            answer_question(
                question
            )


        except Exception as e:

            print(
                "\nUnexpected error:"
            )

            print(
                str(e)
            )