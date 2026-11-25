# Overleaf Draft Specification

## Purpose
Specifies the structure, formatting requirements, and MCP-assisted tooling for the IEEE conference LaTeX paper draft.

## ADDED Requirements

### Requirement: IEEE Conference LaTeX Formatting
The system SHALL provide a complete, self-contained LaTeX project adhering to the official two-column `IEEEtran` conference template, including `main.tex`, `references.bib`, and high-resolution system figures.

#### Scenario: Compiling IEEE conference draft
- **WHEN** `main.tex` is compiled using pdfLaTeX or XeLaTeX on Overleaf
- **THEN** it generates a standard IEEE two-column manuscript without syntax errors, missing citations, or undefined references

### Requirement: MCP-Assisted Overleaf Authoring and Inspection
The system SHALL define an MCP (Model Context Protocol) integration interface allowing AI assistants to query Overleaf compile logs, inspect LaTeX source files, and apply targeted text and citation edits.

#### Scenario: Querying compiler diagnostics via MCP
- **WHEN** an agent triggers the Overleaf MCP compilation tool
- **THEN** the MCP server returns compiler exit status, error lines, and warnings in structured JSON format
