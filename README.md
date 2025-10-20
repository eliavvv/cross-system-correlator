# Cross-System Event Correlator

A small, usable command-line tool that parses heterogeneous logs (API, DB, storage) and correlates events that belong to the same logical operation. It outputs grouped event chains with a confidence score.

# Quickstart
Local (Python 3.10+)

python -m venv .venv && source .venv/bin/activate # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m correlator.cli correlate \
--api sample-logs/api.log \
--db sample-logs/db.log \
--storage sample-logs/storage.log \
--date 2025-09-30 \
--window 60 \
--format text

# Docker

Build the image (run this once in the project root)
docker build -t correlator .

Run the container (Linux/macOS)
docker run --rm -it -v "$(pwd)/sample-logs:/app/sample-logs" correlator \
  correlate --api sample-logs/api.log --db sample-logs/db.log --storage sample-logs/storage.log \
  --date 2025-09-30 --window 60 --format text

Run the container (Windows PowerShell)
docker run --rm -it -v "${PWD}\sample-logs:/app/sample-logs" correlator `
  correlate --api sample-logs/api.log --db sample-logs/db.log --storage sample-logs/storage.log `
  --date 2025-09-30 --window 60 --format text


# CLI

python -m correlator.cli correlate \
--api <path> --db <path> --storage <path> \
[--date YYYY-MM-DD] [--window SECONDS] [--format text|json] [--show-orphans]

# 🧩 CLI Installation (Optional)

To install the command globally inside your virtual environment:
pip install -e .

Then you can simply run:
correlator correlate --api sample-logs/api.log --db sample-logs/db.log --storage sample-logs/storage.log --date 2025-09-30 --format text

# Example Output

Chain: req_816 (initiated by bob)
[09:32:05] API | bob | GET /dashboard/stats
[09:32:06] DB | dashboard_svc | SQL SELECT metric, current_value FROM dashboard_stats
[09:32:08] STORAGE | dashboard_svc | READ cache/dashboard_stats.json (8 KB)
Correlation: HIGH (avg score 1.55)
