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
# 3. Questions for evaluation
# ==========================================

questions = [
    "Who developed thornless Khejri?",
    "Who created traditional Bhili dolls?",
    "Who developed the water-and-electricity welding machine?",
    "Who developed the hand-operated Mahua seed-breaking machine?",
    "Who provides free soldier physical training?"
]


# ==========================================
# 4. Test retrieval
# ==========================================

for question in questions:

    print("\n")
    print("=" * 80)
    print("QUESTION:", question)
    print("=" * 80)

    # Create embedding for question
    query_embedding = model.encode(
        [question],
        normalize_embeddings=True
    ).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3
    )

    # Display top 3 results
    for i in range(len(results["documents"][0])):

        print(f"\n--- Result {i + 1} ---")

        print(results["documents"][0][i])

        print("\nMetadata:")
        print(results["metadatas"][0][i])

        print("\nDistance:")
        print(results["distances"][0][i])