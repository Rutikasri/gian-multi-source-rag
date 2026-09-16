import chromadb
from sentence_transformers import SentenceTransformer


# ==========================================
# 1. Load embedding model
# ==========================================

print("Loading embedding model...")

model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

print("Embedding model loaded.")


# ==========================================
# 2. Connect to ChromaDB
# ==========================================

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_collection(
    name="gian_knowledge"
)

print(f"Records in collection: {collection.count()}")


# ==========================================
# 3. Questions
# ==========================================

questions = [
    "Who developed thornless Khejri?",
    "Who created traditional Bhili dolls?",
    "Who developed the water-and-electricity welding machine?",
    "Who developed the hand-operated Mahua seed-breaking machine?",
    "Who provides free soldier physical training?"
]


# ==========================================
# 4. Relationship keywords
# ==========================================

relationship_keywords = {
    "developed": [
        "developed",
        "developed/tested"
    ],
    "created": [
        "created",
        "creates"
    ],
    "founded": [
        "founded"
    ]
}


# ==========================================
# 5. Determine expected relationship
# ==========================================

def detect_relationship(question):

    question_lower = question.lower()

    for relationship, keywords in relationship_keywords.items():

        for keyword in keywords:

            if keyword in question_lower:
                return relationship

    return None


# ==========================================
# 6. Reranking function
# ==========================================

def rerank(question, results):

    expected_relationship = detect_relationship(question)

    candidates = []

    for i in range(len(results["documents"][0])):

        document = results["documents"][0][i]
        metadata = results["metadatas"][0][i]
        distance = results["distances"][0][i]

        # Lower distance = better semantic similarity
        semantic_score = 1 / (1 + distance)

        rerank_score = semantic_score

        # ----------------------------------
        # Give relationship records a boost
        # ----------------------------------

        if metadata.get("record_kind") == "relationship":

            rerank_score += 0.25

        # ----------------------------------
        # Match relationship type
        # ----------------------------------

        relationship_type = str(
            metadata.get("relationship_type", "")
        ).lower()

        if expected_relationship:

            if expected_relationship in relationship_type:

                rerank_score += 0.50

        candidates.append({
            "document": document,
            "metadata": metadata,
            "distance": distance,
            "score": rerank_score
        })

    # Highest score first
    candidates.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return candidates


# ==========================================
# 7. Run evaluation
# ==========================================

for question in questions:

    print("\n")
    print("=" * 80)
    print("QUESTION:", question)
    print("=" * 80)

    query_embedding = model.encode(
        [question],
        normalize_embeddings=True
    ).tolist()

    # Retrieve more candidates before reranking
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=10
    )

    reranked = rerank(
        question,
        results
    )

    # Display top 3 after reranking
    print("\nRERANKED RESULTS:")

    for i, result in enumerate(reranked[:3]):

        print(f"\n--- Result {i + 1} ---")

        print(result["document"])

        print("\nMetadata:")
        print(result["metadata"])

        print("\nOriginal distance:")
        print(result["distance"])

        print("\nRerank score:")
        print(result["score"])