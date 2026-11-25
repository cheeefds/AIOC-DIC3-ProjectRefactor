# Spec Delta: ICEIB Paper Sections Specification (A-to-Z Style)

## Purpose
Defines the required structural sections, rhetorical nodes, and IEEE conference style compliance rules for the ICEIB academic paper following the A-to-Z writing methodology.

## ADDED Requirements

### Requirement: A-to-Z Abstract Structure
The paper abstract SHALL adhere to the 6-part A-to-Z abstract structure (Attention Getter/Motivation, But/Challenge, Cure/Proposed Solution, Development/Methodology, Experiments/Evaluation, and Findings/Outcomes) within a single paragraph compliant with IEEE conference word limits ($\le 250$ words).

#### Scenario: Verify abstract rhetorical elements
- **WHEN** the abstract section is compiled
- **THEN** it explicitly states the WHO public health burden, the ACL 2025 LLM numerical hallucination challenge, the Tool-augmented Evidence Agent proposal, the $(SiteId, DataCreationDate)$ composite key, the 60-question Taiwan benchmark, and the empirical audit findings on 970,296 raw rows.

### Requirement: A-to-Z Introduction Flow
The Introduction section SHALL follow the 6-stage logical progression: General context (G), However problem definition (H), In-literature model survey (I), Judgement and SWOT trade-offs (J), Keypoint contributions (K), and List of manuscript organization (L).

#### Scenario: Verification of introduction contributions
- **WHEN** reading Section I (Introduction)
- **THEN** it explicitly enumerates the 4 primary contributions: (1) reproducible data preparation, (2) deterministic analytics suite and Evidence Guard, (3) 60-question localized benchmark, and (4) comparative empirical validation.

### Requirement: A-to-Z Related Work Synthesis and Summary Table
The Related Work section SHALL categorize relevant prior work into distinct methodological families, formulate an explicit Research Gap regarding Taiwan AQI question answering, and present a standardized 6-column Article Summary Table.

#### Scenario: Literature summary table formatting
- **WHEN** Section II (Related Work) is rendered
- **THEN** it includes Table I with columns `Study`, `Dataset / Scope`, `AI / Statistical Method`, `Domain Focus`, `Primary Finding`, and `Limitation in Local Context`, covering foundational references [1] through [8].

### Requirement: A-to-Z Proposed Design Decomposition (PA~PM)
The Proposed Design section SHALL incorporate the 13 foundational module blocks: Aim (PA), Background (PB), Cure (PC), Design shift (PD), Paper elements (PE), Formulation (PF), Graph (PG), How (PH), Implementation (PI), Jump to example (PJ), Key points and limits (PK), Later simulation (PL), and Math proof (PM).

#### Scenario: Inclusion of formal algorithm and domain rules
- **WHEN** Section IV (System Architecture and Methodology) is examined
- **THEN** it details the 9-stage operational pipeline, enforces the composite key $(SiteId, DataCreationDate)$, and provides Algorithm 1 with exactly 14 numbered execution lines.

### Requirement: A-to-Z Experiment and Simulation Framework
The Experiment section SHALL define quantitative metrics (Quality and Quantity), evaluate three comparative configurations (LLM-only, Deterministic Tools, Proposed Agent), specify the 60-item benchmark setup (45 answerable + 15 abstention), analyze tuning parameters/failure cases, and tabulate useful performance results.

#### Scenario: Comparative evaluation metrics verification
- **WHEN** Section V and VI (Evaluation and Results) are compiled
- **THEN** it presents Table II documenting Numerical Accuracy, Provenance Fidelity, Unsupported-claim Rate, and Abstention Accuracy across all three modes.

### Requirement: A-to-Z Conclusion Formulation
The Conclusion section SHALL synthesize the research across the 4 A-to-Z closing dimensions: What proposed (W), eXcel domain strengths (X), Yields tangible outputs (Y), and Zen philosophical boundaries and future work (Z).

#### Scenario: Validation of concluding remarks
- **WHEN** the final section is read
- **THEN** it summarizes the decoupling of language from arithmetic, states the open-source artifacts, and details the future roadmap for real-time AQX_P_432 API and IoT sensor integration.

### Requirement: IEEE ICEIB Conference Style Compliance
The manuscript SHALL strictly adhere to the official IEEE two-column conference formatting guidelines (`\documentclass[conference]{IEEEtran}`), including IEEE-style bibliography formatting and standard typographical conventions.

#### Scenario: LaTeX syntax and reference compliance
- **WHEN** `main.tex` is compiled against `references.bib`
- **THEN** all citations resolve without errors, and the document renders in standard two-column IEEE conference layout.
