# Change: DIC4 Overleaf Draft for IEEE Conference using MCP and OpenSpec on GitHub

## 1. Problem Statement
Following the successful completion of the DIC3 prototype and benchmark implementation, the Taiwan Air Quality Evidence Agent project transitions into DIC4 (Conference Paper Drafting & CI/CD Spec Integration). The team requires:
1. A standard camera-ready IEEE conference paper draft formatted in LaTeX (`IEEEtran.cls`), ready to be synced with Overleaf, with complete integration of the A~F research storyline, the 5 core design principles, the 3 architectural trade-offs, and empirical findings.
2. A streamlined bridge between local development, AI agents, and Overleaf using Model Context Protocol (MCP) servers and GitHub integration.
3. Spec-Driven Development (OpenSpec) operationalized directly on GitHub via automated GitHub Actions CI workflows, pull-request-driven spec verification, and version-controlled system specifications.

## 2. Proposed Changes
- **Overleaf Draft Suite**: Create `myplane/overleaf_draft/` containing `main.tex` and `references.bib`, formatted to two-column IEEE conference standards with zero external image dependencies for instant clean compilation.
- **MCP Overleaf Integration**: Provide configuration and operational protocols for connecting Model Context Protocol (MCP) servers to Overleaf and Git repositories, enabling autonomous agents to read LaTeX build errors, edit paper sections, and verify citations.
- **GitHub OpenSpec Pipeline**: Deploy GitHub Actions CI workflow (`.github/workflows/openspec-verify.yml`) to automatically validate OpenSpec changes and main specifications on every branch push and pull request.
- **OpenSpec Lifecycle Synchronization**: Synchronize all baseline capabilities into `openspec/specs/` and establish this DIC4 change artifact set for full transparency on GitHub.

## 3. Impact Assessment
- **Deliverables**: IEEE LaTeX manuscript ready for publication submission, Overleaf MCP tooling specification, GitHub Actions CI verification.
- **Scope**: Documentation, LaTeX source, MCP integration guides, and CI configuration. No destructive changes to core python analytics engine.
