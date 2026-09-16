import os
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# 1. Paths
# ============================================================

DATA_DIR = "data"
CHROMA_DIR = "chroma_db"

SOURCE1_FILE = os.path.join(DATA_DIR, "source1_entities.csv")
SOURCE2_FILE = os.path.join(DATA_DIR, "source2_entities.csv")
RELATIONSHIPS_FILE = os.path.join(DATA_DIR, "relationships.csv")
GIAN_FILE = os.path.join(DATA_DIR, "gian_nidhi.csv")


# Official source URLs from the assignment
SOURCE1_URL = (
    "https://drive.google.com/file/d/"
    "1cS7fMCNjoyD1qnZCC5wOwRUDypQVHX0Z/view"
)

SOURCE2_URL = (
    "https://drive.google.com/file/d/"
    "1D0WbXe75Cn1ow9RcPOSAqMGJ9pPFIw-o/view"
)

GIAN_URL = "https://gian.org/gian-nidhi/"


# ============================================================
# 2. Load data
# ============================================================

print("=" * 70)
print("LOADING DATA")
print("=" * 70)

source1 = pd.read_csv(SOURCE1_FILE, dtype=str).fillna("")
source2 = pd.read_csv(SOURCE2_FILE, dtype=str).fillna("")
relationships = pd.read_csv(
    RELATIONSHIPS_FILE,
    dtype=str
).fillna("")
gian = pd.read_csv(
    GIAN_FILE,
    dtype=str
).fillna("")


print(f"Source 1 records: {len(source1)}")
print(f"Source 2 records: {len(source2)}")
print(f"Relationship records: {len(relationships)}")
print(f"GIAN Nidhi records: {len(gian)}")


# ============================================================
# 3. Combine Shodhyatra entities
# ============================================================

entities = pd.concat(
    [source1, source2],
    ignore_index=True
)

print(f"\nTotal Shodhyatra entities: {len(entities)}")


# ============================================================
# 4. Create entity lookup
# ============================================================

entity_lookup = {}

for _, row in entities.iterrows():

    record_id = str(row["record_id"])

    entity_lookup[record_id] = {
        "person_name": str(row["person_name"]),
        "entity_type": str(row["entity_type"]),
        "innovation": str(row["innovation_or_knowledge"]),
        "location": str(row["location"]),
        "source": str(row["source"]),
        "page": str(row["page"]),
        "confidence": str(row["evidence_confidence"])
    }


print(
    f"Entity lookup created: "
    f"{len(entity_lookup)} entities"
)


# ============================================================
# 5. Load embedding model
# ============================================================

print("\n" + "=" * 70)
print("LOADING EMBEDDING MODEL")
print("=" * 70)

MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

model = SentenceTransformer(MODEL_NAME)

print(f"Embedding model: {MODEL_NAME}")
print("Embedding model loaded.")


# ============================================================
# 6. Create fresh ChromaDB collection
# ============================================================

print("\n" + "=" * 70)
print("CREATING CHROMADB")
print("=" * 70)

client = chromadb.PersistentClient(
    path=CHROMA_DIR
)

try:
    client.delete_collection(
        name="gian_knowledge"
    )

    print("Old collection removed.")

except Exception:
    print("No previous collection found.")


collection = client.create_collection(
    name="gian_knowledge"
)

print("New collection created.")


# ============================================================
# 7. Storage lists
# ============================================================

documents = []
metadatas = []
ids = []


# ============================================================
# 8. Add Shodhyatra entity records
# ============================================================

print("\n" + "=" * 70)
print("ADDING SHODHYATRA ENTITY RECORDS")
print("=" * 70)

for _, row in entities.iterrows():

    record_id = str(row["record_id"])
    person_name = str(row["person_name"])
    entity_type = str(row["entity_type"])
    innovation = str(row["innovation_or_knowledge"])
    location = str(row["location"])
    source = str(row["source"])
    page = str(row["page"])
    confidence = str(row["evidence_confidence"])

    # Select the official URL based on source.
    if source == "51st Shodhyatra":
        source_url = SOURCE1_URL
        document_title = "51st Shodhyatra"
    elif source == "53rd Shodhyatra Presentation":
        source_url = SOURCE2_URL
        document_title = "53rd Shodhyatra Presentation"
    else:
        source_url = ""
        document_title = ""

    text = (
        f"Person/Entity: {person_name}. "
        f"Entity type: {entity_type}. "
        f"Innovation or knowledge: {innovation}. "
        f"Location: {location}. "
        f"Source: {source}. "
        f"Page: {page}."
    )

    documents.append(text)

    metadatas.append({
        "record_id": record_id,
        "person": person_name,
        "entity_type": entity_type,
        "location": location,
        "source": source,
        "source_url": source_url,
        "document_title": document_title,
        "page": page,
        "confidence": confidence,
        "record_kind": "entity"
    })

    ids.append(record_id)


print(
    f"Shodhyatra entity records added: "
    f"{len(entities)}"
)


# ============================================================
# 9. Add linked relationship records
# ============================================================

print("\n" + "=" * 70)
print("ADDING RELATIONSHIP RECORDS")
print("=" * 70)

linked_count = 0
unlinked_count = 0

for _, row in relationships.iterrows():

    relationship_id = str(
        row["relationship_id"]
    )

    source_entity_id = str(
        row["source_entity_id"]
    )

    source_entity_type = str(
        row["source_entity_type"]
    )

    relationship_type = str(
        row["relationship_type"]
    )

    target_entity = str(
        row["target_entity"]
    )

    target_entity_type = str(
        row["target_entity_type"]
    )

    confidence = str(
        row["confidence"]
    )

    evidence_record = str(
        row["evidence_record"]
    )

    source = str(
        row["source"]
    )

    page = str(
        row["page"]
    )

    # -----------------------------------------
    # Find source entity
    # -----------------------------------------

    entity = entity_lookup.get(
        source_entity_id
    )

    if entity:

        person_name = entity["person_name"]
        location = entity["location"]

        linked_count += 1

    else:

        # Never invent missing entity names.
        person_name = "Unknown entity"
        location = ""

        unlinked_count += 1


    # -----------------------------------------
    # Select official source URL
    # -----------------------------------------

    if source == "51st Shodhyatra":
        source_url = SOURCE1_URL
        document_title = "51st Shodhyatra"

    elif source == "53rd Shodhyatra Presentation":
        source_url = SOURCE2_URL
        document_title = "53rd Shodhyatra Presentation"

    else:
        source_url = ""
        document_title = ""


    # -----------------------------------------
    # Relationship text
    # -----------------------------------------

    text = (
        f"Person/Entity: {person_name}. "
        f"Relationship: {relationship_type}. "
        f"Target: {target_entity}. "
        f"Target type: {target_entity_type}. "
        f"Location: {location}. "
        f"Evidence record: {evidence_record}. "
        f"Source: {source}. "
        f"Page: {page}. "
        f"Confidence: {confidence}."
    )

    documents.append(text)

    metadatas.append({
        "record_id": relationship_id,
        "person": person_name,
        "entity_type": "relationship",
        "location": location,
        "source": source,
        "source_url": source_url,
        "document_title": document_title,
        "page": page,
        "confidence": confidence,
        "record_kind": "relationship",
        "source_entity_id": source_entity_id,
        "source_entity_type": source_entity_type,
        "target_entity": target_entity,
        "target_entity_type": target_entity_type,
        "relationship_type": relationship_type
    })

    ids.append(relationship_id)


print(f"Linked relationships: {linked_count}")
print(f"Unlinked relationships: {unlinked_count}")


# ============================================================
# 10. Add ALL 640 GIAN Nidhi records
# ============================================================

print("\n" + "=" * 70)
print("ADDING GIAN NIDHI RECORDS")
print("=" * 70)

gian_count = 0

for _, row in gian.iterrows():

    record_id = str(row["record_id"]).strip()

    if not record_id:
        continue


    # -----------------------------------------
    # Read the CLEANED CSV columns
    # -----------------------------------------

    project_id = str(
        row["id"]
    ).strip()

    sr_no = str(
        row["sr_no"]
    ).strip()

    column_status = str(
        row["column_status"]
    ).strip()

    project_name = str(
        row["project_name"]
    ).strip()

    participants = str(
        row["participants"]
    ).strip()

    abstract = str(
        row["abstract"]
    ).strip()

    college_status = str(
        row["college_status"]
    ).strip()


    # -----------------------------------------
    # Don't create empty project records
    # -----------------------------------------

    if not project_name:
        continue


    # -----------------------------------------
    # Create searchable document
    # -----------------------------------------

    text = (
        f"GIAN Nidhi project: {project_name}. "
        f"Project ID: {project_id}. "
        f"Sr No: {sr_no}. "
        f"Status: {column_status}. "
        f"Participants: {participants}. "
        f"Abstract: {abstract}. "
        f"College: {college_status}. "
        f"Source: GIAN Nidhi. "
        f"Source URL: {GIAN_URL}."
    )


    documents.append(text)


    # -----------------------------------------
    # Metadata
    # -----------------------------------------

    metadatas.append({
        "record_id": record_id,
        "project_id": project_id,
        "sr_no": sr_no,
        "project_name": project_name,
        "person": participants,
        "participants": participants,
        "college": college_status,
        "source": "GIAN Nidhi",
        "source_url": GIAN_URL,
        "document_title": "GIAN Nidhi",
        "data_category": "GIAN Nidhi Project",
        "page": "",
        "confidence": "source",
        "record_kind": "gian_nidhi"
    })


    ids.append(record_id)

    gian_count += 1


print(
    f"GIAN Nidhi records added: "
    f"{gian_count}"
)


# ============================================================
# 11. Sanity check BEFORE embeddings
# ============================================================

print("\n" + "=" * 70)
print("SANITY CHECK")
print("=" * 70)

print(
    f"Shodhyatra entities : {len(entities)}"
)

print(
    f"Relationships        : {linked_count}"
)

print(
    f"GIAN Nidhi           : {gian_count}"
)

print(
    f"Total documents      : {len(documents)}"
)

print(
    f"Total metadata       : {len(metadatas)}"
)

print(
    f"Total IDs            : {len(ids)}"
)


if len(documents) != len(metadatas):
    raise RuntimeError(
        "ERROR: documents and metadata counts do not match."
    )

if len(documents) != len(ids):
    raise RuntimeError(
        "ERROR: documents and IDs counts do not match."
    )

if gian_count != 640:
    raise RuntimeError(
        f"ERROR: Expected 640 GIAN Nidhi records, "
        f"but found {gian_count}."
    )

if len(set(ids)) != len(ids):
    raise RuntimeError(
        "ERROR: Duplicate ChromaDB IDs detected."
    )

print("\nSANITY CHECK PASSED.")


# ============================================================
# 12. Generate embeddings
# ============================================================

print("\n" + "=" * 70)
print("GENERATING EMBEDDINGS")
print("=" * 70)

print(
    f"Creating embeddings for "
    f"{len(documents)} records..."
)

embeddings = model.encode(
    documents,
    normalize_embeddings=True,
    show_progress_bar=True
)

embeddings = embeddings.tolist()

print("Embeddings generated.")


# ============================================================
# 13. Store records in ChromaDB
# ============================================================

print("\n" + "=" * 70)
print("STORING RECORDS IN CHROMADB")
print("=" * 70)

collection.add(
    ids=ids,
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas
)

print("Records successfully stored.")


# ============================================================
# 14. Final verification
# ============================================================

print("\n" + "=" * 70)
print("INGESTION COMPLETED")
print("=" * 70)

print(
    f"Shodhyatra entities : {len(entities)}"
)

print(
    f"Linked relationships: {linked_count}"
)

print(
    f"GIAN Nidhi          : {gian_count}"
)

print(
    f"Total records       : {collection.count()}"
)

print(
    f"Collection          : {collection.name}"
)

print(
    f"Database            : {CHROMA_DIR}"
)

print("\nExpected total:")
print(
    f"{len(entities)} + "
    f"{linked_count} + "
    f"{gian_count} = "
    f"{len(entities) + linked_count + gian_count}"
)

print("\nActual total:")
print(collection.count())

if collection.count() == (
    len(entities) +
    linked_count +
    gian_count
):
    print("\nFINAL VERIFICATION: PASSED")
else:
    print("\nFINAL VERIFICATION: FAILED")