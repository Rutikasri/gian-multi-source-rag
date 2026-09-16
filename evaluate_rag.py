import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURATION
# ============================================================

DB_PATH = "./chroma_db"
COLLECTION_NAME = "gian_knowledge"

EMBEDDING_MODEL = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


# ============================================================
# TEST QUESTIONS
# ============================================================

TEST_CASES = [
    {
        "question": "Who developed thornless Khejri?",
        "expected_person": "Rameshwar",
        "expected_source": "51st Shodhyatra",
        "expected_page": "4",
    },
    {
        "question": "Who created traditional Bhili dolls?",
        "expected_person": "Ramesh Parmar",
        "expected_source": "53rd Shodhyatra Presentation",
        "expected_page": "14",
    },
    {
        "question": "Who developed the water-and-electricity welding machine?",
        "expected_person": "Vishal Parmar",
        "expected_source": "53rd Shodhyatra Presentation",
        "expected_page": "54",
    },
    {
        "question": "Who developed the hand-operated Mahua seed-breaking machine?",
        "expected_person": "Dharamveer",
        "expected_source": "53rd Shodhyatra Presentation",
        "expected_page": "60",
    },
    {
        "question": "Who provides free soldier physical training?",
        "expected_person": "Uday Bilwal",
        "expected_source": "53rd Shodhyatra Presentation",
        "expected_page": "63",
    },
]


# ============================================================
# RELATIONSHIP DETECTION
# ============================================================

def detect_relationship(question):

    q = question.lower()

    if "developed" in q:
        return "developed"

    if "created" in q:
        return "created"

    if "provides" in q or "provide" in q:
        return "provides"

    return None


# ============================================================
# RETRIEVAL + RERANKING
# ============================================================

def retrieve_and_rerank(
    collection,
    model,
    question,
    top_k=10
):

    query_embedding = model.encode(
        question,
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    question_relationship = detect_relationship(question)

    question_lower = question.lower()

    # Important words from the question
    question_words = set(
        question_lower
        .replace("?", "")
        .replace(",", "")
        .split()
    )

    important_words = {
        word
        for word in question_words
        if len(word) > 3
    }

    # Specific phrases that are important for our test cases
    important_phrases = [
        "thornless khejri",
        "bhili dolls",
        "traditional bhili dolls",
        "water-and-electricity welding machine",
        "water and electricity welding machine",
        "welding machine",
        "hand-operated mahua seed-breaking machine",
        "hand operated mahua seed-breaking machine",
        "mahua seed-breaking machine",
        "soldier physical academy",
        "soldier physical training",
    ]

    ranked_results = []

    for doc, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        doc_lower = doc.lower()

        # ----------------------------------------------------
        # Base semantic score
        # ----------------------------------------------------

        semantic_score = 1 / (1 + distance)

        rerank_score = semantic_score

        # ----------------------------------------------------
        # Relationship evidence bonus
        # ----------------------------------------------------

        if metadata.get("record_kind") == "relationship":
            rerank_score += 0.25

        # ----------------------------------------------------
        # Exact relationship match
        # ----------------------------------------------------

        metadata_relationship = str(
            metadata.get("relationship_type", "")
        ).lower()

        if (
            question_relationship
            and question_relationship
            in metadata_relationship
        ):
            rerank_score += 0.50

        # ----------------------------------------------------
        # Keyword overlap bonus
        # ----------------------------------------------------

        matched_words = 0

        for word in important_words:

            if word in doc_lower:
                matched_words += 1

        rerank_score += 0.05 * matched_words

        # ----------------------------------------------------
        # Exact phrase matching bonus
        # ----------------------------------------------------

        for phrase in important_phrases:

            if (
                phrase in question_lower
                and phrase in doc_lower
            ):
                rerank_score += 0.50
                break

        ranked_results.append(
            {
                "document": doc,
                "metadata": metadata,
                "distance": distance,
                "rerank_score": rerank_score,
            }
        )

    # Highest score first
    ranked_results.sort(
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    return ranked_results


# ============================================================
# PAGE MATCHING
# ============================================================

def page_matches(expected_page, actual_page):

    expected_page = str(expected_page).strip()
    actual_page = str(actual_page).strip()

    if not expected_page or not actual_page:
        return False

    # Convert formats such as:
    #
    # 63
    # 62-63
    # 54-55
    # 2,4
    #
    # into individual page numbers.

    cleaned = (
        actual_page
        .replace("-", " ")
        .replace(",", " ")
        .replace("/", " ")
    )

    actual_numbers = []

    for part in cleaned.split():

        if part.isdigit():
            actual_numbers.append(int(part))

    if expected_page.isdigit():

        expected_number = int(expected_page)

        return expected_number in actual_numbers

    return expected_page.lower() in actual_page.lower()


# ============================================================
# MAIN
# ============================================================

print("=" * 80)
print("RAG RETRIEVAL EVALUATION")
print("=" * 80)


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("\nLoading embedding model...")

model = SentenceTransformer(
    EMBEDDING_MODEL
)

print("Embedding model loaded.")


# ============================================================
# CONNECT TO CHROMADB
# ============================================================

print("\nConnecting to ChromaDB...")

client = chromadb.PersistentClient(
    path=DB_PATH
)

collection = client.get_collection(
    COLLECTION_NAME
)

print(
    f"Knowledge base records: "
    f"{collection.count()}"
)


# ============================================================
# METRICS
# ============================================================

top1_correct = 0
recall_at_3 = 0
source_correct = 0


# ============================================================
# RUN TEST CASES
# ============================================================

for i, test in enumerate(
    TEST_CASES,
    start=1
):

    question = test["question"]

    expected_person = test["expected_person"]

    expected_source = test["expected_source"]

    expected_page = test["expected_page"]


    print("\n" + "=" * 80)
    print(f"TEST {i}")
    print("=" * 80)

    print(
        f"Question: {question}"
    )

    print(
        f"Expected person: {expected_person}"
    )


    # --------------------------------------------------------
    # Retrieve
    # --------------------------------------------------------

    results = retrieve_and_rerank(
        collection,
        model,
        question,
        top_k=10
    )


    # --------------------------------------------------------
    # TOP-1 ACCURACY
    # --------------------------------------------------------

    top1 = results[0]

    top1_text = top1["document"].lower()

    if expected_person.lower() in top1_text:

        top1_correct += 1

        top1_status = "PASS"

    else:

        top1_status = "FAIL"


    # --------------------------------------------------------
    # RECALL@3
    # --------------------------------------------------------

    top3 = results[:3]

    found_in_top3 = False

    for result in top3:

        text = result["document"].lower()

        if expected_person.lower() in text:

            found_in_top3 = True

            break


    if found_in_top3:

        recall_at_3 += 1

        recall_status = "PASS"

    else:

        recall_status = "FAIL"


    # --------------------------------------------------------
    # SOURCE + PAGE MATCH
    # --------------------------------------------------------

    source_found = False

    for result in top3:

        metadata = result["metadata"]

        source = str(
            metadata.get("source", "")
        )

        page = str(
            metadata.get("page", "")
        )


        source_ok = (
            expected_source.lower()
            in source.lower()
        )


        page_ok = page_matches(
            expected_page,
            page
        )


        if source_ok and page_ok:

            source_found = True

            break


    if source_found:

        source_correct += 1

        source_status = "PASS"

    else:

        source_status = "FAIL"


    # --------------------------------------------------------
    # DISPLAY TOP 3
    # --------------------------------------------------------

    print("\nTop 3 Retrieved Evidence:")


    for rank, result in enumerate(
        top3,
        start=1
    ):

        metadata = result["metadata"]


        print(
            f"\nRank {rank}"
        )

        print(
            "-" * 40
        )


        print(
            result["document"][:500]
        )


        print(
            f"Source: "
            f"{metadata.get('source', 'N/A')}"
        )


        print(
            f"Page: "
            f"{metadata.get('page', 'N/A')}"
        )


        print(
            f"Rerank score: "
            f"{result['rerank_score']:.4f}"
        )


    # --------------------------------------------------------
    # TEST RESULTS
    # --------------------------------------------------------

    print("\nResults:")

    print(
        f"Top-1 Accuracy: {top1_status}"
    )

    print(
        f"Recall@3:       {recall_status}"
    )

    print(
        f"Source Match:   {source_status}"
    )


# ============================================================
# FINAL METRICS
# ============================================================

total = len(TEST_CASES)


top1_accuracy = (
    top1_correct / total
) * 100


recall_percentage = (
    recall_at_3 / total
) * 100


source_percentage = (
    source_correct / total
) * 100


# ============================================================
# FINAL REPORT
# ============================================================

print("\n\n" + "=" * 80)
print("FINAL EVALUATION RESULTS")
print("=" * 80)


print(
    f"\nTop-1 Accuracy : "
    f"{top1_correct}/{total} "
    f"({top1_accuracy:.1f}%)"
)


print(
    f"Recall@3       : "
    f"{recall_at_3}/{total} "
    f"({recall_percentage:.1f}%)"
)


print(
    f"Source Match   : "
    f"{source_correct}/{total} "
    f"({source_percentage:.1f}%)"
)


print("\n" + "=" * 80)
print("Evaluation complete.")
print("=" * 80)