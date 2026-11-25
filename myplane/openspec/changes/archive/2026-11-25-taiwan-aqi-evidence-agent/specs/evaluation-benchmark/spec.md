## ADDED Requirements

### Requirement: Fixed 60-Question Benchmark Suite
The system SHALL provide a standardized test suite consisting of exactly 60 curated questions covering four distinct categories: 15 trend queries, 15 station comparison queries, 15 AQI/pollutant interpretation queries, and 15 data-limitation/unsupported queries.

#### Scenario: Running test suite execution
- **WHEN** the benchmark evaluation script is executed
- **THEN** all 60 benchmark items are loaded and evaluated against ground truth values derived from deterministic reference queries

### Requirement: Multi-Condition Comparative Evaluation
The system SHALL run the benchmark across three evaluation conditions: (1) LLM-only direct answering, (2) Deterministic Tools tabular output, and (3) Tool-augmented Evidence Agent.

#### Scenario: Multi-condition benchmarking
- **WHEN** evaluation script runs in comparative mode
- **THEN** system logs responses and structured outputs across all three conditions for every test item

### Requirement: Quantitative Metric Assessment
The system SHALL compute quantitative metrics for all runs: Numerical Answer Accuracy, Provenance Fidelity, Unsupported-claim Rate, and Limitation/Abstention Accuracy.

#### Scenario: Metric calculation and reporting
- **WHEN** all benchmark evaluations complete
- **THEN** system outputs a summary score report comparing all three conditions across the defined metrics and generates an error taxonomy breakdown

