# GIAN AI Data Research & Knowledge Engineering

## 1. Project Overview

This project implements an AI-ready, multi-source knowledge base and Retrieval-Augmented Generation (RAG) system for the GIAN AI Data Research & Knowledge Engineering assignment.

The system combines information from:

1. The 51st Shodhyatra source document
2. The 53rd Shodhyatra source document
3. GIAN Nidhi structured project data

The main focus is on data analysis, cleaning, entity and relationship structuring, source traceability, semantic retrieval, vector storage, and grounded question answering.

The system is designed so that answers are generated only from retrieved source evidence and do not intentionally introduce unsupported names, relationships, dates, awards, technical details, or other facts.

---

## 2. Main Objectives

The project addresses the following requirements:

- Analyse heterogeneous source data
- Extract and structure entities and relationships
- Clean and deduplicate GIAN Nidhi records
- Preserve source attribution and metadata
- Create an AI-ready structured knowledge base
- Generate embeddings for semantic retrieval
- Store records in ChromaDB
- Retrieve relevant information for user questions
- Use an LLM to generate source-grounded answers
- Reduce hallucination by restricting the generation prompt to retrieved evidence
- Provide traceability through source, page, record, and URL information
- Provide a simple Streamlit interface for querying the knowledge base

---

## 3. Data Sources

### Source 1 — 51st Shodhyatra

The source covers the 51st Shodhyatra conducted in Rajasthan.

Official/source document URL:

https://drive.google.com/file/d/1cS7fMCNjoyD1qnZCC5wOwRUDypQVHX0Z/view

The extracted structured data is stored in:

```text
data/source1_entities.csv
```

### Source 2 — 53rd Shodhyatra

The source covers the 53rd Shodhyatra across Madhya Pradesh and Gujarat.

Official/source document URL:

https://drive.google.com/file/d/1D0WbXe75Cn1ow9RcPOSAqMGJ9pPFIw-o/view

The extracted structured data is stored in:

```text
data/source2_entities.csv
```

Relationships identified during analysis are stored in:

```text
data/relationships.csv
```

### Source 3 — GIAN Nidhi

GIAN Nidhi is the structured project repository used in this project.

Source URL:

https://gian.org/gian-nidhi/

The cleaned dataset contains 640 unique project records.

The final structured dataset is:

```text
data/gian_nidhi.csv
```

The raw extracted dataset is retained separately for auditability:

```text
data/gian_nidhi_raw.csv
```

---

## 4. GIAN Nidhi Data Processing

The GIAN Nidhi website displayed duplicate rows while being extracted.

The extraction process collected:

- 1,280 raw rows
- 640 unique project IDs
- Each project ID appeared twice
- The repeated records were exact duplicates
- No repeated ID contained conflicting data

Therefore, one copy of each exact duplicate was retained.

The cleaned dataset contains:

```text
640 unique records
```

The cleaning process also handled a small number of transparent structural anomalies observed in the source HTML.

No missing information was invented.

Missing values remain empty when the source does not provide the information.

The cleaning scripts are:

```text
extract_gian_nidhi.py
validate_gian_nidhi.py
clean_gian_nidhi.py
```

---

## 5. Structured Data

### GIAN Nidhi CSV fields

The cleaned GIAN Nidhi dataset contains:

```text
record_id
id
column_status
sr_no
project_name
participants
abstract
college_status
source
source_url
data_category
```

The `record_id` provides a stable internal identifier such as:

```text
GN-001
GN-002
...
GN-640
```

The original project ID from GIAN Nidhi is retained separately.

Participants are preserved as participants. They are not automatically treated as innovators or developers unless the source explicitly supports such a relationship.

---

## 6. Entity and Relationship Structure

The Shodhyatra data is structured around entities such as:

- People
- Innovations
- Activities
- Organisations
- Publications
- Events
- Locations
- Source documents

Relationships are stored separately where a relationship is explicitly supported by the source.

For example, relationships can represent source-supported associations such as:

```text
Person -> developed -> Innovation
Person -> associated with -> Activity
Person -> practices -> Technique
```

Relationships are not inferred merely because two names or concepts appear similar.

This is important for avoiding unsupported entity linking.

---

## 7. Metadata and Source Traceability

The vector records include metadata to support traceability.

Depending on the source and availability of information, metadata includes fields such as:

```text
record_id
project_id
sr_no
project_name
participants
college
source
source_url
document_title
data_category
page
confidence
record_kind
```

For Shodhyatra records, page information is retained where available.

For GIAN Nidhi records, the GIAN Nidhi source URL and project/record identifiers are retained.

The system is designed to show the source information associated with retrieved evidence.

---

## 8. Embeddings

The embedding model used for semantic retrieval is:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

The same embedding model is used during ingestion and retrieval.

This provides vector representations of the structured records for semantic similarity search.

---

## 9. Vector Database

The project uses **ChromaDB** as the persistent vector database for storing
the embedded knowledge records used during retrieval.

A **pre-built ChromaDB vector database is included in the GitHub repository**
for independent evaluation.

The persistent database is stored in:

```text
chroma_db/

The collection name is:

```text
gian_knowledge
```

The current database contains:

```text
53 Shodhyatra entity records
10 relationship records
640 GIAN Nidhi records
--------------------------------
703 total records
```
### Loading the Pre-built Vector Database

The included ChromaDB can be loaded directly without rebuilding it:

```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("gian_knowledge")

print("Collection:", collection.name)
print("Record count:", collection.count())
```
Expected output:
Collection: gian_knowledge
Record count: 703

The ingestion script recreates the collection and performs sanity checks before completing.

---

## 10. Ingestion Pipeline

The main ingestion script is:

```text
ingest.py
```

The pipeline performs the following operations:

```text
Structured source data
        |
        v
Load CSV files
        |
        v
Validate records
        |
        v
Create source-aware text
        |
        v
Generate embeddings
        |
        v
Store records in ChromaDB
        |
        v
Run sanity checks
        |
        v
703 records stored
```

The ingestion process verifies:

- Expected record counts
- Unique record IDs
- Metadata count
- Shodhyatra entity count
- Relationship count
- GIAN Nidhi record count
- Final ChromaDB collection count

---

## 11. Retrieval and RAG Pipeline

The main RAG implementation is:

```text
rag.py
```

The retrieval pipeline is:

```text
User Question
      |
      v
Question analysis
      |
      v
Structured / semantic retrieval
      |
      v
ChromaDB retrieval
      |
      v
Source-aware reranking
      |
      v
Relevant evidence
      |
      v
Grounded LLM prompt
      |
      v
Answer + source traceability
```

The retrieval layer supports explicit GIAN Nidhi queries such as:

- Project ID lookup
- Project name lookup
- Participant-to-project lookup
- College/location-to-project lookup

It also supports semantic retrieval for Shodhyatra information and relationship-oriented questions.

---

## 12. LLM

The generation model used through the Groq API is:

```text
openai/gpt-oss-20b
```

The generation temperature is set to:

```text
0
```

This is used to make the response generation more deterministic.

The API key is loaded from an environment variable and is not stored in the source code.

---

## 13. Anti-Hallucination Approach

The RAG system uses a strict system prompt instructing the LLM to:

- Answer only from supplied evidence
- Not use outside knowledge
- Not invent names
- Not invent dates
- Not invent awards
- Not invent relationships
- Not invent locations
- Not invent technical details
- Not invent sources
- Prefer direct evidence
- Mention relevant source information
- State when the available evidence is insufficient

When the sources do not contain enough information, the intended response is:

> The available sources do not provide sufficient information to answer this.

This approach is used because source attribution and factual traceability are important requirements of the assignment.

---

## 14. Streamlit Application

The user interface is implemented using:

```text
Streamlit
```

The main application file is:

```text
app.py
```

The interface provides:

- Project title and description
- Source information
- Knowledge-base record count
- Model information
- Example questions
- Question input
- Enter-to-submit functionality
- Generated answer
- Source traceability information

---

## 15. Project Structure

```text
gian-rag/
│
├── app.py
├── rag.py
├── ingest.py
├── hybrid_query.py
│
├── extract_gian_nidhi.py
├── validate_gian_nidhi.py
├── clean_gian_nidhi.py
│
├── requirements.txt
├── README.md
├── data_analysis_report.md
├── evaluation_examples.md
│
├── data/
│   ├── gian_nidhi.csv
│   ├── gian_nidhi_raw.csv
│   ├── source1_entities.csv
│   ├── source2_entities.csv
│   └── relationships.csv
│
└── chroma_db/
```

The exact contents of the final submission may differ depending on whether the local ChromaDB is included or rebuilt using the ingestion script.

---

## 16. Installation

Create and activate a Python virtual environment.

On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the required packages:

```powershell
pip install -r requirements.txt
```

The main dependencies are:

```text
chromadb
pandas
python-dotenv
sentence-transformers
groq
streamlit
selenium
```

---

## 17. Environment Configuration

Create a `.env` file in the project root:

```text
GROQ_API_KEY=your_groq_api_key
```

Do not commit the actual API key to GitHub or include it in the submission ZIP.

A `.gitignore` file should exclude:

```text
.env
venv/
__pycache__/
```

---

## 18. Build / Rebuild the Vector Database

After the cleaned datasets are available, run:

```powershell
python ingest.py
```

A successful ingestion should report approximately:

```text
Shodhyatra entities : 53
Relationships        : 10
GIAN Nidhi           : 640
Total documents      : 703
```

The script performs final verification before completing.

---

## 19. Run the RAG Application

Start the Streamlit application with:

```powershell
streamlit run app.py --server.fileWatcherType none
```

The application will provide a local Streamlit address in the terminal.

Open that address in a browser.

---

## 20. Example Questions

Examples of supported questions include:

```text
What is project ID 640?
```

```text
Which project is associated with Belgi Akanksha Manoj?
```

```text
What is the 360 Metallurgy Flexible Drilling Machine project?
```

```text
Which projects are associated with Government Polytechnic Miraj?
```

```text
Who developed the thornless Khejri technique?
```

```text
Who developed the water-and-electricity welding machine?
```

These questions test direct retrieval, entity linking, college/project association, and source-supported relationship retrieval.

---

## 21. Evaluation

Evaluation examples are documented separately in:

```text
evaluation_examples.md
```

The evaluation covers:

- Direct fact retrieval
- Project ID retrieval
- Project name retrieval
- Participant-to-project linking
- College-to-project linking
- Innovator/innovation retrieval where supported by the source
- Source attribution
- Cross-document relationship retrieval
- Multi-source retrieval
- Missing-information handling
- Anti-hallucination behaviour

The expected answers are based on the structured source records rather than unsupported external knowledge.

---

## 22. Data Analysis Report

The data analysis and modelling decisions are documented in:

```text
data_analysis_report.md
```

The report describes:

- Understanding of all three sources
- Data formats
- Entities
- Relationships
- Linking fields
- Data gaps
- Cleaning decisions
- Deduplication
- Metadata
- Source attribution
- Limitations and assumptions

---

## 23. Important Data Integrity Decisions

The following principles were followed throughout the project:

1. Do not fabricate missing values.
2. Do not infer a relationship from a similar name alone.
3. Do not automatically label GIAN Nidhi participants as innovators.
4. Preserve source wording where possible.
5. Remove exact duplicate GIAN Nidhi records.
6. Keep the raw extracted GIAN Nidhi data for auditability.
7. Store source URLs with structured records.
8. Preserve page information for document-based records where available.
9. Use explicit identifiers for records and projects.
10. Keep retrieval and generation grounded in the stored evidence.

---

## 24. Limitations

- Some source records contain missing fields.
- Some source relationships are not explicitly stated and therefore are not inferred.
- GIAN Nidhi is a web-based source and its displayed table structure required deduplication and limited structural cleaning.
-  A pre-built ChromaDB is included in the GitHub repository for independent evaluation. It can also be rebuilt using `ingest.py`.
- The quality of generated answers depends on the quality and coverage of retrieved evidence.
- Semantic retrieval may return additional context for broad questions; explicit structured matching is used where a query contains identifiable GIAN Nidhi entities such as project IDs, project names, participants, or colleges.

---

## 25. Reproducibility

A fresh setup can be reproduced by:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Then configure:

```text
.env
```

with the Groq API key.

Build the vector database:

```powershell
python ingest.py
```

Run the application:

```powershell
streamlit run app.py --server.fileWatcherType none
```

---

## 26. Security

The following should not be included in the public repository or shared submission:

```text
.env
GROQ_API_KEY
```

The API key should always be supplied through an environment variable.

---

## 27. Summary

This project provides a complete multi-source data-to-RAG pipeline:

```text
Shodhyatra PDFs + GIAN Nidhi
             |
             v
       Data Extraction
             |
             v
     Cleaning & Validation
             |
             v
    Entity / Relationship
         Structuring
             |
             v
       Source Metadata
             |
             v
        Embeddings
             |
             v
          ChromaDB
             |
             v
     Structured Retrieval
       + Semantic Search
             |
             v
       Grounded RAG
             |
             v
       Streamlit UI
```

The implementation prioritizes structured data, entity linking, source traceability, reproducibility, and evidence-grounded answers rather than treating the project as only a chatbot.
