import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# 1. Load embedding model
# ============================================================

MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

print("Loading embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Embedding model loaded.")


# ============================================================
# 2. Connect to ChromaDB
# ============================================================

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_collection(
    name="gian_knowledge"
)

print(
    f"Collection records: {collection.count()}"
)


# ============================================================
# 3. GIAN Nidhi test questions
# ============================================================

questions = [

    "What is the 360 Metallurgy Flexible Drilling Machine?",

    "Who are the participants of the Continuous Variable Transmission project?",

    "Which college is associated with the Continuous Variable Transmission project?",

    "What is the Automatic Lime Line Marking Machine for Different Sports Grounds?",

    "Who participated in the Multipurpose Mechanical Machine project?",

    "What is project ID 639 in GIAN Nidhi?",

    "Which project is associated with Government Polytechnic Miraj?",

    "What information is available for project ID 640?"
]


# ============================================================
# 4. Retrieve results
# ============================================================

for question in questions:

    print("\n")
    print("=" * 80)
    print("QUESTION:")
    print(question)
    print("=" * 80)

    query_embedding = model.encode(
        [question],
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=5
    )

    for i in range(
        len(results["documents"][0])
    ):

        document = results["documents"][0][i]
        metadata = results["metadatas"][0][i]
        distance = results["distances"][0][i]

        print(
            f"\nResult {i + 1}"
        )

        print("-" * 80)

        print(document)

        print("\nMetadata:")
        print(metadata)

        print(
            f"\nDistance: {distance:.4f}"
        )