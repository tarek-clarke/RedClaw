# RedClaw: Containerized Browser Agent
FROM mcr.microsoft.com/playwright/python:v1.40.0-focal

# Set working directory
WORKDIR /app

# Copy project files
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

# Copy rest of the code
COPY . .

# Ensure standard data files exist (even as placeholders)
RUN touch user_profile.json resume.pdf .env

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Entry point
ENTRYPOINT ["python", "main.py"]
