# RedClaw: Trustworthy, Local-First Browser Agent for Job Applications

RedClaw is a production-grade, privacy-first autonomous agent designed to handle the complexity and sensitivity of job applications. Engineered specifically for **AMD GPUs** (ROCm) and **LM Studio**, it puts the human in control with a robust "Action Plan" and "Audit Log" architecture.

## Why RedClaw?

In a world of black-box AI agents, RedClaw prioritizes **trust, transparency, and local execution**.
- **Local-Only**: Your profile, resume, and credentials never leave your machine. All reasoning happens via your local LM Studio instance.
- **Human-in-the-Loop (HITL)**: RedClaw acts as a co-pilot. It proposes action plans for your approval and escalates ambiguous fields to you in real-time.
- **Auditability**: Every run generates a structured JSONL audit log, capturing every observation, decision, and approval.
- **AMD Focused**: Optimized for Radeon hardware (e.g., 7900 XT) via local GGUF models (Gemma 4 & gpt-oss-20b).

## Key Features

- **Action Plan Preview**: Approves a human-readable roadmap before a single browser action is taken.
- **Dry-Run Mode**: Simulate full application flows without clicking final submission buttons.
- **Safety Policy Layer**: Configurable domain whitelists and mandatory pauses for logins/uploads.
- **Site Adapters**: Modular support for major hiring platforms (Greenhouse, Lever, etc.) for high-precision form filling.
- **Job-Fit Preflight**: Automatically scores how well your resume matches a job description before starting.
- **Persistent Sessions**: Securely reuse browser logins for approved sites without re-authenticating.

## Security & Trust Model

| Feature | Behavior |
| :--- | :--- |
| **Data Storage** | All personal data (`user_profile.json`, `resume.pdf`) is strictly local and Git-ignored. |
| **Connectivity** | 0% Cloud dependency. Connects only to your specified LM Studio host. |
| **Submission** | **Never** clicks "Submit" without explicit human approval. |
| **Audit Logs** | Structured logs record all agent actions, screenshots, and user approvals. |
| **File Access** | Restricted to the application directory and specific whitelisted local paths. |

## Quickstart

### 1. Requirements
- Python 3.10+
- LM Studio running with **Gemma 4** (Vision) and **gpt-oss-20b** (Reasoning).
- (Windows users) Double-click `run.bat`
- (Mac/Linux users) Run `./run.sh`

### 2. Configure Your Profile
Rename `user_profile.example.json` to `user_profile.json` and add your career highlights and links.

### 3. Usage
```bash
python main.py --goal "Apply for the Senior Machine Learning Engineer role at [Company Name]" --url "[Link]"
```

## Dry-Run Mode
Use the `--dry-run` flag to test an entire application flow. The agent will navigate, extract, and fill data but will **always pause** before final submission.

## Architecture
RedClaw uses a modular **Adapter-Strategy** pattern:
1. **Preflight**: Scores job-fit and prepares answers.
2. **Planning**: Proposes a multi-step roadmap.
3. **Execution**: Uses **Playwright** with site-specific adapters for high reliability.
4. **Audit**: Logs every step to `logs/run_ID.jsonl`.

---
*RedClaw is built by the community for private, ethical AI automation.*
