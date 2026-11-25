# Design: ICEIB Academic Paper Architecture following A-to-Z SOP

## 1. Conference Target and Template Standard
- **Target Venue**: ICEIB (International Conference on Environmental Informatics and Biotechnology).
- **Manuscript Class**: `IEEEtran.cls`, two-column `conference` mode (`\documentclass[conference]{IEEEtran}`).
- **Format Requirements**: Single title block, author affiliations, abstract, index terms, numbered major sections in Roman numerals (`I. INTRODUCTION`, etc.), uppercase subsection headers, IEEE citation style (`\cite{...}` with numeric brackets), and standard two-column tabular environments.

## 2. A-to-Z Academic Writing Methodology Architecture
The paper architecture directly maps the 26 logical stages of the A-to-Z academic writing SOP (`A2Z.docx`) into the required 7 IEEE conference sections:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   ICEIB IEEE Paper & A-to-Z Mapping                    │
├─────────────────────┬──────────────────────────────────────────────────┤
│ Section             │ A-to-Z SOP Subsections / Logical Nodes           │
├─────────────────────┼──────────────────────────────────────────────────┤
│ I. Abstract         │ [A] Attention Getter (Motivation)                │
│                     │ [B] But (Challenge)                              │
│                     │ [C] Cure (Proposed Solution)                     │
│                     │ [D] Development (Methodology)                    │
│                     │ [E] Experiments (Evaluation Setup)               │
│                     │ [F] Findings (Preliminary Audit & Expected Gain) │
├─────────────────────┼──────────────────────────────────────────────────┤
│ II. Introduction    │ [G] General (Environmental AI Status Quo)        │
│                     │ [H] However (Problem Definition & RAG/LLM Limits)│
│                     │ [I] In literature (3 AI/Model Categories)        │
│                     │ [J] Judgement (SWOT: Regression vs. Agent QA)    │
│                     │ [K] Keypoint (Core Contributions 1-4)            │
│                     │ [L] List of Organization (Manuscript Roadmap)    │
├─────────────────────┼──────────────────────────────────────────────────┤
│ III. Related Work   │ [M] Methods (8 Papers: Neuro-Air, SVC, DTW, etc.)│
│                     │ [N] New Proposed (Research Gap Definition)       │
│                     │ [O] Organized (6-Column Literature Summary Table)│
├─────────────────────┼──────────────────────────────────────────────────┤
│ IV. Proposed Design │ [PA] Aim (Traceable Taiwan AQI QA)               │
│     (Scheme)        │ [PB] Background (MOENV AQX_P_488 Clean Corpus)   │
│                     │ [PC] Cure / Cause (Separation of Text & Compute) │
│                     │ [PD] Design Transfer (From Chatbot to Tool Agent)│
│                     │ [PE] Paper Elements (9-Stage Processing Pipeline)│
│                     │ [PF] Formulation (Planner, Quality, Analytics)   │
│                     │ [PG] Graph (Mermaid Flow & Pipeline Hierarchy)   │
│                     │ [PH] How (Composite Key (SiteId, CreationDate))  │
│                     │ [PI] Implementation (14-Step Pseudocode Alg. 1)  │
│                     │ [PJ] Jump to Example (3 Representative Use Cases)│
│                     │ [PK] Key Points & Limits (Domain Guardrails)     │
│                     │ [PL] Later Simulation (IoT / Real-time API Ext.) │
│                     │ [PM] Math Proof (Deterministic AQI Max Sub-index)│
├─────────────────────┼──────────────────────────────────────────────────┤
│ V. Experiment and   │ [Q] Quality & Quantity Metrics (Acc., Fidelity)  │
│    Evaluation       │ [R] Related Methods to Compare (3 Modes)         │
│                     │ [S] Simulation Setup (60-Question Benchmark)     │
│                     │ [T] Tuning Parameters (Error Taxonomy Analysis)  │
│                     │ [U] Useful Results (Empirical Performance Table) │
├─────────────────────┼──────────────────────────────────────────────────┤
│ VI. Conclusion      │ [W] What Proposed (Summary of Tool-Agent)        │
│                     │ [X] eXcel (Domain Specialization & Auditability) │
│                     │ [Y] Yields (Cleaned Records, Isolated Conflicts) │
│                     │ [Z] Zen (Philosophical Boundary & Future Work)   │
├─────────────────────┼──────────────────────────────────────────────────┤
│ References          │ IEEE-Compliant BibTeX Database ([1]–[14])        │
└─────────────────────┴──────────────────────────────────────────────────┘
```

## 3. Section Detailed Design Specifications

### Section 1: Abstract (A ~ F)
- **Constraint**: Strict IEEE single-paragraph format, between 180 and 240 words.
- **Content**: Covers WHO health impact (A), LLM hallucination and local regulatory mismatch (B), Tool-augmented Evidence Agent proposal (C), decoupling and composite key mechanism (D), 60-question Taiwan benchmark (E), and 970k data audit / 13 conflict isolation findings (F).

### Section 2: Introduction (General to List)
- **General & However**: Establishes Taiwan's MOENV open data environment and contrasts it with the ACL 2025 finding of 3%–86% LLM hallucination rate.
- **In Literature & Judgement**: Reviews prediction and calibration papers, identifying that high accuracy on numbers does not yield traceable natural language answers.
- **Keypoint & Organization**: Clearly states the 4 key contributions and outlines the paper's roadmap.

### Section 3: Related Work (Methods, Gap, Summary Table)
- **Summary Table**: Standard 6-column matrix (Study, Dataset, AI Method, Domain Focus, Primary Finding, Limitation in Local Context) covering literature [1] through [8].
- **Research Gap**: Formulates the gap in evaluating Taiwan AQI time-series question answering with row-level citation verification.

### Section 4: Proposed Design (PA ~ PM)
- **Architecture**: Incorporates the 5 Core Design Principles and 3 Architectural Trade-offs.
- **Components**: Documents the 9 operational processing stages.
- **Algorithm**: Integrates Algorithm 1 with 14 numbered execution lines.

### Section 5: Experiment and Simulation (Quality to Useful Results)
- **Metrics**: Answer Accuracy, Provenance Fidelity, Unsupported-claim Rate, and Limitation/Abstention Accuracy.
- **Configurations**: Mode 1 (LLM-only), Mode 2 (Deterministic Tools Only), Mode 3 (Proposed Agent).
- **Benchmark**: Exactly 45 answerable queries and 15 adversarial abstention cases.

### Section 6: Conclusion (What to Zen)
- **What & eXcel**: Reaffirms the core novelty: separation of natural language synthesis from deterministic arithmetic.
- **Yields & Zen**: Highlights reproducible open data artifacts and emphasizes adherence to evidence boundaries.

### References
- Complete IEEE references for [1] through [14].
