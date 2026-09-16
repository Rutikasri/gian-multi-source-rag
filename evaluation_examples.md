# Evaluation Examples

## GIAN AI Data Research & Knowledge Engineering

This document records representative evaluation questions used to test the multi-source knowledge base and RAG pipeline.

The examples cover direct fact retrieval, entity linking, project/participant relationships, organisation-to-project retrieval, source attribution, and source-grounded Shodhyatra relationship retrieval.

---

## 1. Evaluation Approach

The system was tested using questions from both the structured GIAN Nidhi dataset and the Shodhyatra sources.

The evaluation focuses on:

- Retrieval accuracy
- Entity recognition
- Project ID lookup
- Project name lookup
- Participant-to-project linking
- College-to-project linking
- Person-to-innovation relationship retrieval
- Source attribution
- Page/record traceability
- Grounded answer generation
- Avoiding unsupported relationships

The expected answer is based on the available structured records and source documents.

---

# 2. Direct GIAN Nidhi Project ID Retrieval

## Question

```text
What is project ID 640?
```

## Query type

Direct project ID lookup.

## Expected retrieved record

```text
Record ID: GN-640
Project ID: 640
Project Name: Induced Draft Pulling Tower System
Participants: Patel Rakesh, Sandhansi Pradeep, Shah Milan, Tambhake Mayur
College: Bhagvan Mahavir polytechnic
Source: GIAN Nidhi
```

## Retrieval result

The structured GIAN Nidhi lookup returned exactly one matching record:

```text
GN-640
```

## Expected answer characteristics

The answer should identify the project as:

```text
Induced Draft Pulling Tower System
```

and cite GIAN Nidhi as the source.

The answer should not invent additional project details that are not present in the retrieved record.

---

# 3. Direct GIAN Nidhi Project ID Retrieval

## Question

```text
What is project ID 639?
```

## Query type

Direct project ID lookup.

## Expected retrieved record

```text
Record ID: GN-639
Project ID: 639
Project Name: Pedal Power Hacksaw
Source: GIAN Nidhi
```

## Retrieval result

The structured lookup returned exactly one matching record:

```text
GN-639
```

## Expected answer characteristics

The answer should identify:

```text
Pedal Power Hacksaw
```

as the project associated with project ID 639.

---

# 4. Project Name Retrieval

## Question

```text
What is the 360 Metallurgy Flexible Drilling Machine project?
```

## Query type

Exact project-name retrieval.

## Expected retrieved record

```text
Record ID: GN-001
Project ID: 1
Project Name: 360 METALLURGY FLEXIBLE DRILLING MACHINE
Source: GIAN Nidhi
```

## Retrieval result

The project-name matching logic returned exactly one matching GIAN Nidhi record:

```text
GN-001
```

## Expected answer characteristics

The answer should be based on the GIAN Nidhi record and should not add technical specifications unless they are present in the retrieved abstract.

---

# 5. Project Name Retrieval

## Question

```text
What is Continuous Variable Transmission?
```

## Query type

Exact project-name retrieval.

## Expected retrieved record

```text
Record ID: GN-004
Project ID: 4
Project Name: CONTINUOUS VARIABLE TRANSMISSION
Participants: Belgi Akanksha Manoj
College: Government Polytechnic Miraj
Source: GIAN Nidhi
```

## Retrieval result

The project-name lookup returned one record:

```text
GN-004
```

---

# 6. Participant-to-Project Entity Linking

## Question

```text
Which project is associated with Belgi Akanksha Manoj?
```

## Query type

Participant → project lookup.

## Expected retrieved record

```text
Record ID: GN-004
Project ID: 4
Project Name: CONTINUOUS VARIABLE TRANSMISSION
Participant: Belgi Akanksha Manoj
College: Government Polytechnic Miraj
Source: GIAN Nidhi
```

## Retrieval result

The participant matching logic returned exactly one record:

```text
GN-004
```

## Expected answer characteristics

The answer should say that the participant is associated with:

```text
CONTINUOUS VARIABLE TRANSMISSION
```

according to the GIAN Nidhi record.

It should not change the relationship into an unsupported claim such as "developed by" unless an appropriate source explicitly states that relationship.

---

# 7. Project-to-Participant Retrieval

## Question

```text
Who are the participants of Continuous Variable Transmission?
```

## Query type

Project → participants lookup.

## Expected retrieved record

```text
Record ID: GN-004
Project ID: 4
Project Name: CONTINUOUS VARIABLE TRANSMISSION
Participants: Belgi Akanksha Manoj
Source: GIAN Nidhi
```

## Retrieval result

The structured project lookup returned one record:

```text
GN-004
```

## Expected answer

The answer should identify the participant listed in the GIAN Nidhi record:

```text
Belgi Akanksha Manoj
```

---

# 8. College-to-Project Retrieval

## Question

```text
Which projects are associated with Government Polytechnic Miraj?
```

## Query type

College/location → projects lookup.

## Expected result count

```text
7 records
```

## Expected project records

| Project ID | Project Name |
|---:|---|
| 4 | CONTINUOUS VARIABLE TRANSMISSION |
| 64 | Tricycle Fitted With Windmill Reducing Effort Of Pedallers |
| 302 | Clay Cool (Zero power Refrigerator) |
| 395 | Low cost solar water heater |
| 429 | Tricycle Fitted With Windmill Reducing Effort Of Pedallers |
| 439 | Clay Cool (zero Power Refrigerator) |
| 540 | Low Cost Solar Water Heater |

## Retrieval result

The college/location matching logic returned exactly the seven records above.

## Data-quality observation

The result demonstrates why generic words such as:

```text
Government
Polytechnic
```

should not be treated as sufficient entity matches.

The retrieval logic instead identifies the requested location:

```text
Miraj
```

and matches it against the college field.

---

# 9. Project ID to College Retrieval

## Question

```text
Which college is associated with project ID 4?
```

## Query type

Project ID → college lookup.

## Expected retrieved record

```text
Record ID: GN-004
Project ID: 4
Project Name: CONTINUOUS VARIABLE TRANSMISSION
College: Government Polytechnic Miraj
Source: GIAN Nidhi
```

## Expected answer

The answer should identify:

```text
Government Polytechnic Miraj
```

as the college in the GIAN Nidhi record.

---

# 10. Shodhyatra Relationship Retrieval — Thornless Khejri

## Question

```text
Who developed the thornless Khejri technique?
```

## Query type

Relationship / innovation retrieval.

## Expected source-supported answer

The available Shodhyatra evidence identifies:

```text
Rameshwar Lal / Rameshwar Prasad Ji
```

in connection with grafting Khejri to make it thornless.

## Source

```text
51st Shodhyatra
```

## Page information

```text
Pages 2 and 4
```

## Expected answer characteristics

The answer should identify the person using the source-supported wording and explain the associated activity without adding unsupported technical claims.

The source should be explicitly attributed.

---

# 11. Shodhyatra Relationship Retrieval — Welding Machine

## Question

```text
Who developed the water-and-electricity welding machine?
```

## Query type

Relationship / innovation retrieval.

## Expected source-supported answer

The 53rd Shodhyatra source identifies:

```text
Vishal Parmar
```

in connection with the welding machine using water/electricity.

## Source

```text
53rd Shodhyatra
```

## Page information

```text
Pages 54–55
```

## Expected answer characteristics

The answer should identify Vishal Parmar and cite the 53rd Shodhyatra source.

The answer should not add engineering specifications that are not present in the retrieved evidence.

---

# 12. Missing Information Test

## Purpose

The system should also be tested with questions for which the available sources do not contain sufficient evidence.

Example:

```text
What award did a particular GIAN Nidhi participant receive?
```

if the retrieved GIAN Nidhi record does not contain an award.

## Expected behaviour

The system should not invent an award.

The appropriate response is:

```text
The available sources do not provide sufficient information to answer this.
```

This test verifies the anti-hallucination requirement.

---

# 13. Unsupported Relationship Test

## Question pattern

```text
Who developed [GIAN Nidhi project]?
```

when the available GIAN Nidhi record only contains a participant field and does not explicitly state a developer relationship.

## Expected behaviour

The system should distinguish:

```text
participant
```

from:

```text
developer / innovator
```

and should not automatically convert the participant relationship into a development claim.

If the source does not establish the requested relationship, the answer should state that sufficient information is not available.

---

# 14. Entity-Linking Test

## Question pattern

```text
Is the person with the same/similar name in the two Shodhyatra sources the same person?
```

## Expected behaviour

The system should not automatically merge the records based only on name similarity.

A cross-source identity should require sufficient source-supported evidence.

If the available sources do not establish the identity, the answer should state that the sources do not provide sufficient information to confirm the relationship.

---

# 15. Evaluation Summary

The tested retrieval cases demonstrate the following capabilities:

| Capability | Example |
|---|---|
| Project ID lookup | Project ID 640 |
| Project ID lookup | Project ID 639 |
| Project name lookup | 360 Metallurgy Flexible Drilling Machine |
| Project name lookup | Continuous Variable Transmission |
| Participant → project | Belgi Akanksha Manoj |
| Project → participants | Continuous Variable Transmission |
| College → projects | Government Polytechnic Miraj |
| Project → college | Project ID 4 |
| Innovation → person | Thornless Khejri |
| Innovation → person | Water-and-electricity welding machine |
| Missing information handling | Unsupported award query |
| Relationship safety | Participant ≠ automatically developer |
| Entity-linking safety | Similar names are not automatically merged |

---

# 16. Evaluation Principles

The evaluation follows these principles:

1. Prefer exact structured matches when the question contains an explicit project ID.
2. Prefer exact project-name matching when a project name is identifiable.
3. Use participant and college fields for supported entity-to-record retrieval.
4. Use semantic retrieval for conceptual Shodhyatra questions.
5. Preserve source attribution.
6. Preserve page or record identifiers where available.
7. Do not infer relationships from name similarity alone.
8. Do not convert participant information into an unsupported developer/innovator claim.
9. Do not fabricate missing information.
10. When evidence is insufficient, explicitly state that the available sources do not provide sufficient information.

---

# 17. Conclusion

The evaluation examples demonstrate the intended behaviour of the GIAN multi-source RAG system across heterogeneous data.

The system combines:

```text
Structured matching
+
Semantic retrieval
+
Entity-aware retrieval
+
Source metadata
+
Grounded LLM generation
```

The evaluation is designed to test not only whether the chatbot produces an answer, but whether the answer is supported by the underlying structured data and can be traced back to its source.
