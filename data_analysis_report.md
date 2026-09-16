# Data Analysis Report
## GIAN AI Data Research & Knowledge Engineering Assignment

---

## 1. Introduction

This project develops an AI-ready multi-source knowledge base and Retrieval-Augmented Generation (RAG) system using three heterogeneous GIAN-related sources:

1. 51st Shodhyatra source document
2. 53rd Shodhyatra source document
3. GIAN Nidhi project repository

The data analysis stage focuses on understanding the structure and meaning of each source before retrieval and generation. Particular attention was given to entity identification, relationship linking, source attribution, missing information, duplicate records, standardization, and preservation of source traceability.

The central design principle is:

> **Do not infer facts or relationships that are not supported by the available source data.**

---

# 2. Source Inventory

## 2.1 Source 1 — 51st Shodhyatra

### Source type
PDF / document-based source.

### Coverage
The document describes the 51st Shodhyatra conducted in Rajasthan, including innovators, local practices, agricultural techniques, traditional knowledge, prototypes, and other observations.

### Source URL

https://drive.google.com/file/d/1cS7fMCNjoyD1qnZCC5wOwRUDypQVHX0Z/view

### Structured representation

The extracted information is represented in:

```text
data/source1_entities.csv
```

Relevant source metadata includes the source name, document title, page information where available, entity/record identifier, category, and source URL.

### Examples of explicitly documented entities

Examples include:

- Rameshwar Lal / Rameshwar Prasad Ji — grafting Khejri to make it thornless
- Sundaram Ji / Sunda Ram Verma — tree-growing technique using limited water
- Santosh Pachar — new carrot variety
- Rahulchand / Rawalchand Panchariya — sweet potato varieties
- Dharamveer Khambojji — electric wheelchair and fruit juices
- Rajaram Tak — solar-system model
- Shravan Kumar Soni — bonsai/greening home spaces
- Prahalad — Khejri conservation/cultivation
- Vishnu — archery training for tribal-community students

These are stored as source-supported records rather than as generalized assumptions.

---

# 3. Source 2 — 53rd Shodhyatra

## Source type

PDF / presentation-based source.

## Coverage

The document covers the 53rd Shodhyatra across Madhya Pradesh and Gujarat and contains information about traditional knowledge, art, agriculture, education, social initiatives, prototypes, and local innovations.

The document covers Jhabua and Alirajpur in Madhya Pradesh and Chhota Udepur in Gujarat.

## Source URL

https://drive.google.com/file/d/1D0WbXe75Cn1ow9RcPOSAqMGJ9pPFIw-o/view

## Structured representation

The extracted information is represented in:

```text
data/source2_entities.csv
```

Explicitly identified relationships are stored separately in:

```text
data/relationships.csv
```

## Examples of source-supported entities

Examples include:

- Ramesh Parmar and Shanti Parmar — traditional Bhili dolls/tribal toys
- Subhash Gidwani — Adivasi Gudiya
- Bharti Soni — clay idol making
- Archana Rathwa — Pithora art as an innovative business
- Shivkumarji — Gatha Smriti-Falak / tribal memory pillars
- Santosh Basod — bamboo products and durable broom
- Bhuri Bai — Bhil artist and Pithora art adapted to paper/acrylic
- Sejal Rathwa — banana-fiber diaries
- Surendrapalsingh Chauhan — sunflower selection
- Isak Mansuri — Noorjahan mango
- Vishal Parmar — welding machine using water/electricity
- Dharamveer — hand-operated Mahua seed-breaking machine
- Uday Bilwal — Soldier Physical Academy
- Seema Trivedi — activity-based learning
- Renu Kachhawa — teaching-learning material/playful learning
- Jagdishbhai Makwana — Bhavai folk theatre
- Dineshbhai Rathwa — Rathwa-language word booklet for teachers

---

# 4. Source 3 — GIAN Nidhi

## Source type

Web-based structured table.

## Source URL

https://gian.org/gian-nidhi/

GIAN Nidhi is a repository of projects carried out by ITI and Polytechnic students.

The website provides structured fields including:

```text
ID
Column Status
Sr No
Project Name
Participants
Abstracts
College Status
```

The cleaned representation is:

```text
data/gian_nidhi.csv
```

The raw extraction is retained as:

```text
data/gian_nidhi_raw.csv
```

---

# 5. GIAN Nidhi Extraction and Deduplication

The website extraction produced:

```text
Raw rows:              1,280
Unique project IDs:      640
```

Each project ID appeared twice in the extracted table.

Validation showed:

- Every ID occurred exactly twice.
- The two records for each ID were exact duplicates.
- No repeated ID had conflicting field values.
- IDs covered the complete range from 1 to 640.

Therefore, one copy of each exact duplicate was retained.

Final dataset:

```text
640 unique project records
```

This process was implemented through:

```text
extract_gian_nidhi.py
validate_gian_nidhi.py
clean_gian_nidhi.py
```

The raw file was preserved so that the cleaning process remains auditable.

---

# 6. GIAN Nidhi Cleaning Decisions

The cleaning process was deliberately conservative.

## 6.1 Duplicate records

Exact duplicate rows were deduplicated by project ID after validation confirmed that the duplicate records contained the same data.

## 6.2 Missing values

Missing source information was not fabricated.

After cleaning, the following fields still contain missing values:

```text
participants:    10
abstract:        17
college_status:  55
```

Blank values therefore represent unavailable source information rather than an assumed value.

## 6.3 Structural anomalies

A small number of records contained clear HTML/table extraction anomalies.

For IDs:

```text
162
168
169
171
172
173
174
175
199
```

the extracted college field contained paragraph-like project-description text while the abstract field was empty. These values were moved to the abstract field because the structure of the extracted record clearly indicated that the content belonged there.

For ID:

```text
426
```

the participant field contained the project name itself rather than participant names. That value was cleared from the participant field instead of being treated as a person.

These are structural corrections based on the captured source record. No replacement names or descriptions were invented.

---

# 7. Final GIAN Nidhi Schema

The cleaned dataset contains the following fields:

| Field | Purpose |
|---|---|
| `record_id` | Internal stable record identifier |
| `id` | Original GIAN Nidhi project ID |
| `column_status` | Source table status |
| `sr_no` | Source serial number |
| `project_name` | Project name |
| `participants` | Participants as provided by the source |
| `abstract` | Project abstract/description |
| `college_status` | Associated college information |
| `source` | Source name |
| `source_url` | Original source URL |
| `data_category` | Data classification |

Example internal IDs:

```text
GN-001
GN-002
...
GN-640
```

---

# 8. Entity Analysis

The three sources contain different types of entities.

## 8.1 Person entities

Examples from the Shodhyatra sources include:

```text
Rameshwar Lal / Rameshwar Prasad Ji
Sunda Ram Verma
Ramesh Parmar
Shanti Parmar
Vishal Parmar
Dharamveer
Uday Bilwal
```

GIAN Nidhi contains participant names, but participants are stored as participants rather than automatically classified as innovators.

## 8.2 Innovation / project entities

Examples include:

```text
Thornless Khejri technique
Water-and-electricity welding machine
Hand-operated Mahua seed-breaking machine
Soldier Physical Academy
360 Metallurgy Flexible Drilling Machine
Continuous Variable Transmission
Pedal Power Hacksaw
Induced Draft Pulling Tower System
```

## 8.3 Organisation / institution entities

Examples include:

```text
Government Polytechnic Miraj
Bhagvan Mahavir Polytechnic
Shri Shiv Shivay Farmer Producer Company Ltd.
```

## 8.4 Location entities

Locations occur in both document and structured sources.

Examples include:

```text
Rajasthan
Jhabua
Alirajpur
Chhota Udepur
Miraj
```

## 8.5 Source/document entities

Each source is treated as a first-class source object so that retrieved information can be traced back to its origin.

---

# 9. Relationship Analysis

Relationship extraction is treated separately from simple entity occurrence.

Examples of explicit source-supported relationships include:

```text
Rameshwar Lal -> developed/practiced -> thornless Khejri technique
Vishal Parmar -> developed -> water-and-electricity welding machine
```

The relationship dataset is:

```text
data/relationships.csv
```

The relationship records contain source and page information where available.

## Relationship policy

A relationship is not created simply because:

- two names appear on the same page;
- a person's name resembles another person's name;
- a participant appears next to a project;
- two projects have similar names;
- two institutions share generic words such as "Government Polytechnic".

Only source-supported relationships are represented.

---

# 10. Entity Linking Across Sources

Cross-source entity linking is a major part of the knowledge-base design.

Potential linking fields include:

- Exact person name
- Innovation/project name
- Organisation/college name
- Location
- Source document
- Project ID
- Record ID
- Explicit relationship record

However, similarity alone is not treated as proof of identity.

For example, if the same or similar name appears in two sources, the system does not automatically conclude that both records refer to the same individual.

This reduces false entity linking and unsupported relationships.

---

# 11. Important GIAN Nidhi Linking Decision

GIAN Nidhi contains:

```text
Participants
Project Name
College
Abstract
```

The project does **not** automatically interpret:

```text
participant -> developed -> project
```

because the table itself does not necessarily state that every participant developed the project.

Instead, the data model preserves:

```text
participant -> appears as participant in -> project record
```

unless an explicit source-supported developer relationship is available elsewhere.

This distinction is important for preventing fabricated attribution.

---

# 12. Standardization Decisions

The project uses controlled standardization while preserving original source information.

## Standardized fields

- Stable record IDs
- Project IDs
- Source names
- Source URLs
- Data categories
- Page fields for document records
- Structured relationship types

## Preserved source content

Project names, participant strings, abstracts, and college strings are retained close to their source representation.

The project does not aggressively normalize names because excessive normalization could merge distinct entities incorrectly.

---

# 13. Metadata Design

Metadata is included so that every retrieved record can be traced back to its source.

Important metadata fields include:

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

For document-based records, page information is retained where available.

For GIAN Nidhi records, the original GIAN Nidhi URL and project ID are retained.

---

# 14. AI-Ready Knowledge Representation

The structured data is converted into retrieval-ready text while retaining metadata.

For a GIAN Nidhi record, the retrieval text contains fields such as:

```text
GIAN Nidhi project
Project ID
Serial number
Status
Participants
Abstract
College
Source
Source URL
```

This allows semantic retrieval to use the meaning of the record while metadata allows the result to be traced back to the original source.

---

# 15. Embedding Strategy

The embedding model used is:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

The same model is used during:

```text
Ingestion
    |
    v
Embedding generation
    |
    v
ChromaDB storage
```

and during:

```text
User query
    |
    v
Query embedding
    |
    v
Vector retrieval
```

Using the same model for documents and queries maintains embedding-space compatibility.

---

# 16. Vector Database

The project uses:

```text
ChromaDB
```

Collection:

```text
gian_knowledge
```

Current verified record counts:

| Record type | Count |
|---|---:|
| Shodhyatra entities | 53 |
| Relationship records | 10 |
| GIAN Nidhi records | 640 |
| **Total** | **703** |

The ingestion script performs final sanity checks to confirm the expected counts.

---

# 17. Retrieval Strategy

The retrieval layer combines structured matching and semantic retrieval.

## Structured matching

Used when the query contains identifiable fields such as:

- GIAN Nidhi project ID
- Exact project name
- Participant name
- College/location

Examples:

```text
What is project ID 640?
```

```text
Which project is associated with Belgi Akanksha Manoj?
```

```text
Which projects are associated with Government Polytechnic Miraj?
```

## Semantic retrieval

Used when the question is expressed conceptually or asks about information contained in the Shodhyatra documents.

Examples:

```text
Who developed the thornless Khejri technique?
```

```text
Who developed the water-and-electricity welding machine?
```

The retrieval layer then reranks results using source-aware and entity/relationship signals.

---

# 18. RAG Generation Strategy

The RAG pipeline follows:

```text
Question
   |
   v
Question analysis
   |
   v
Structured / semantic retrieval
   |
   v
Relevant evidence
   |
   v
Source-aware reranking
   |
   v
Grounded prompt
   |
   v
LLM generation
   |
   v
Answer + source traceability
```

The LLM is instructed to use only the retrieved evidence.

---

# 19. Anti-Hallucination Design

The generation prompt explicitly instructs the model not to invent:

- Names
- Dates
- Awards
- Relationships
- Locations
- Technical details
- Sources

The system also instructs the model to state when evidence is insufficient.

The intended missing-information response is:

> The available sources do not provide sufficient information to answer this.

This is preferable to generating a plausible but unsupported answer.

---

# 20. Source Attribution

The expected answer structure includes:

```text
Answer

Relevant Information
- Innovator / person, if supported
- Innovation / project, if supported
- Author, if applicable
- Source
- Page / Record
- URL
```

Multiple sources are kept separate rather than merged into a single unsupported statement.

This makes the answer traceable and allows an evaluator to inspect the original source.

---

# 21. Data Quality Checks

The project includes validation scripts for both retrieval and source data.

### GIAN Nidhi validation

```text
validate_gian_nidhi.py
```

Checks include:

- Total row count
- Unique project IDs
- Duplicate frequency
- Conflicting duplicate data
- Missing values
- ID coverage

### Retrieval evaluation

The project contains:

```text
evaluate_gian_retrieval.py
evaluate_retrieval.py
evaluate_rag.py
evaluate_rag_answers.py
```

These scripts support testing of retrieval and generated answers.

---

# 22. Known Data Gaps

The sources do not provide complete information for every record.

Known GIAN Nidhi missing values after cleaning include:

```text
Participants:    10
Abstract:        17
College:         55
```

The Shodhyatra sources also do not provide identical metadata for every entity.

For example, not every source record necessarily provides:

- Author
- Publication
- Publication year
- Organisation
- Explicit relationship
- Unique external identifier

When such information is unavailable, it is left unavailable rather than inferred.

---

# 23. Limitations

1. The source documents contain heterogeneous narrative information, so not every entity can be represented with identical fields.
2. Some records have missing metadata.
3. Some names or descriptions may appear in multiple contexts without enough evidence to prove identity.
4. GIAN Nidhi participant information does not by itself prove a developer/innovator relationship.
5. The local ChromaDB is generated from the structured source files and can be rebuilt using `ingest.py`.
6. Retrieval quality depends on the quality and coverage of the structured source data.
7. Broad semantic questions can retrieve additional context that may not be directly relevant; structured matching is therefore preferred when an explicit GIAN Nidhi identifier or entity is present.

---

# 24. Reproducibility

The data processing and vector database can be rebuilt using the project scripts.

Main workflow:

```text
Extract
  |
  v
Validate
  |
  v
Clean
  |
  v
Structure
  |
  v
Embed
  |
  v
Store in ChromaDB
  |
  v
Retrieve
  |
  v
Generate grounded answer
```

Main scripts:

```text
extract_gian_nidhi.py
validate_gian_nidhi.py
clean_gian_nidhi.py
ingest.py
rag.py
app.py
```

---

# 25. Final Data Model Summary

The resulting knowledge base can be viewed as four connected layers:

```text
SOURCE LAYER
    |
    +-- 51st Shodhyatra
    +-- 53rd Shodhyatra
    +-- GIAN Nidhi
             |
             v
ENTITY LAYER
    |
    +-- People
    +-- Innovations / Projects
    +-- Organisations
    +-- Locations
    +-- Documents
             |
             v
RELATIONSHIP LAYER
    |
    +-- Explicit source-supported relationships
    +-- Project / participant associations
    +-- Project / college associations
             |
             v
RETRIEVAL LAYER
    |
    +-- Structured search
    +-- Semantic search
    +-- Reranking
    +-- Source metadata
             |
             v
RAG LAYER
    |
    +-- Evidence-only generation
    +-- Source attribution
    +-- Missing-information handling
```

---

# 26. Conclusion

The data preparation stage was designed around the assignment's emphasis on data quality rather than only chatbot functionality.

The final knowledge base:

- combines three heterogeneous GIAN-related sources;
- contains 640 cleaned GIAN Nidhi project records;
- represents Shodhyatra entities and explicit relationships separately;
- preserves source URLs and metadata;
- removes verified exact duplicates;
- retains missing information rather than fabricating values;
- avoids treating participant names as automatic innovator/developer relationships;
- supports structured and semantic retrieval;
- stores 703 verified records in ChromaDB;
- provides source-grounded RAG responses;
- includes evaluation and validation scripts for reproducibility.

The resulting system is therefore designed as a traceable **data → knowledge → retrieval → grounded answer** pipeline rather than as a standalone chatbot.
