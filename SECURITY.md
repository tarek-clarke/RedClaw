# Security Policy for RedClaw

RedClaw is a **privacy-first** tool designed for local execution. Security is at the core of our "Local-Only" architecture.

## Supported Versions
We support the latest version of RedClaw.

## Reporting a Vulnerability
Please report security vulnerabilities through our GitHub Issue tracker.

## Design Patterns
- **No Remote Telemetry**: RedClaw never sends usage data or prompts to a cloud server.
- **Safety Policy**: The agent is restricted to a domain whitelist by default.
- **Human-in-the-Loop**: Critical actions like "Submit" require explicit user approval.
- **Git-Ignored Secrets**: All personal data and keys are kept in files excluded from Git.
