# RedClaw: Local Browser Agent (AMD Optimized)

RedClaw is a privacy-first, local-only browser agent designed to run with **LM Studio** and **AMD GPUs** (ROCm). It uses **Gemma 4** for vision and **gpt-oss-20b** for reasoning, allowing it to navigate the web and fill out forms (like job applications) autonomously while keeping your data strictly on your machine.

## Features
- **AMD Optimized**: Built for Radeon GPUs (e.g., 7900 XT).
- **Multimodal Vision**: Uses Gemma 4 to "see" and understand web pages.
- **Job Application Mode**: Automatically extracts resume data and populates application forms.
- **Privacy-First**: Personal data (resumes, profiles) are stored locally and never committed to Git.
- **HITL (Human-In-The-Loop)**: Pauses for review before critical actions (like clicking "Submit").

## Setup

### 1. Prerequisites
- **LM Studio**: Running on your PC (or local network) with **Gemma 4** and **gpt-oss-20b** models loaded.
- **Python 3.10+**

### 2. Installation
```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configuration
- Rename `.env.example` to `.env` and set your `LM_STUDIO_HOST`.
- (Optional) If LM Studio is on another PC, set `LM_STUDIO_HOST` to `http://<PC_IP>:1234/v1`.
- Rename `user_profile.example.json` to `user_profile.json` and add your details.

### 4. Local Data
Place your `resume.pdf` in the root directory. This file is ignored by Git to protect your privacy.

## Usage

### 1. One-Go Runner (Recommended for Local)
Use the provided bash script to automatically set up your environment, install dependencies, and launch the agent:
```bash
./run.sh
```

### 2. Docker (Containerized)
For a fully isolated environment, use Docker:
```bash
docker build -t redclaw .
docker run -it --env-file .env -v $(pwd)/screenshots:/app/screenshots redclaw --goal "Your job goal" --url "Job URL"
```
*Note: Headed mode in Docker requires additional setup (X11/VNC) to see the browser window.*

### 3. Native Manual Run
Alternatively, you can run the agent manually:
```bash
python main.py --goal "Apply for the Senior Software Engineer position at [Company Name] using my resume" --url "[Job Posting URL]"
```

## Shipping to GitHub (Privacy)
The following files are **Git-ignored** to prevent leaking personal info:
- `user_profile.json`
- `resume.pdf`
- `.env`
- `screenshots/`

Only the generic code and `.example` templates are shared.
