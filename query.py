import chromadb
from sentence_transformers import SentenceTransformer


# Load the same embedding model
model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# Connect to existing ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_collection(
    name="gian_knowledge"
)


# Ask a question
question = "Who developed thornless Khejri?"


# Create query embedding
query_embedding = model.encode(
    [question],
    normalize_embeddings=True
).tolist()


# Search ChromaDB
results = collection.query(
    query_embeddings=query_embedding,
    n_results=5
)


print("\nQUESTION:")
print(question)

print("\nRETRIEVED RESULTS:")
print("=" * 70)

for i in range(len(results["documents"][0])):

    print(f"\nResult {i + 1}")
    print("-" * 70)

    print(results["documents"][0][i])

    print("\nMetadata:")
    print(results["metadatas"][0][i])

    print("\nDistance:")
    print(results["distances"][0][i])