# Contributing to RedClaw

Welcome! We are excited to build a local, private browser agent together. 

## How to Contribute
1. **Report Bugs**: Use the GitHub issue tracker for bug reports.
2. **Standard Adapters**: We welcome new site adapters (e.g., Workday, Ashby). Follow the `BaseAdapter` pattern in `core/adapters/`.
3. **HITL Improvements**: Help us refine the "Human-in-the-Loop" interaction model.

## Principles
- **Privacy-First**: No external logging or cloud-dependency.
- **AMD Optimized**: Maintenance of ROCm/LM Studio compatibility.
- **Trustworthy**: Every browser action must be auditable.

## Development Setup
Follow the Quickstart guide in the README. Use `pytest` for running unit tests.
