# 🧩 Cross-System Event Correlator

A small, production-ready command-line tool that parses **heterogeneous logs** (API, DB, and storage) and **correlates events** that belong to the same logical operation.  
It outputs grouped event chains with a **confidence score**, helping you trace distributed transactions easily.

---

## 🚀 Quickstart (Python 3.10+)

### Windows (PowerShell)
```powershell
# 1. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 3. (Optional) install the package locally to enable the `correlator` CLI
pip install -e .

# 4. Run correlation on sample logs
correlator correlate --api sample-logs\api.log --db sample-logs\db.log --storage sample-logs\storage.log --date 2025-09-30 --window 60 --format text

# If 'correlator' is not recognized:
# python -m correlator.cli correlate --api sample-logs\api.log --db sample-logs\db.log --storage sample-logs\storage.log --date 2025-09-30 --window 60 --format text
```

### macOS / Linux
```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv && source .venv/bin/activate

# 2. Install dependencies
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 3. (Optional) install the package locally to enable the `correlator` CLI
pip install -e .

# 4. Run correlation on sample logs
correlator correlate --api sample-logs/api.log --db sample-logs/db.log --storage sample-logs/storage.log --date 2025-09-30 --window 60 --format text
```

---

## 🐳 Docker

Make sure you have **Docker Desktop** installed and running.

```bash
# Build the image (run this once in the project root)
docker build -t correlator .

# Run the container (Linux/macOS)
docker run --rm -it -v "$(pwd)/sample-logs:/app/sample-logs" correlator \
  correlate --api sample-logs/api.log --db sample-logs/db.log --storage sample-logs/storage.log \
  --date 2025-09-30 --window 60 --format text

# Run the container (Windows PowerShell)
docker run --rm -it -v "${PWD}\sample-logs:/app/sample-logs" correlator correlate `
  --api sample-logs/api.log --db sample-logs/db.log --storage sample-logs/storage.log `
  --date 2025-09-30 --window 60 --format text
```

---

## ⚙️ CLI Reference

```bash
python -m correlator.cli correlate \
  --api PATH_TO_API_LOG \
  --db PATH_TO_DB_LOG \
  --storage PATH_TO_STORAGE_LOG \
  [--date YYYY-MM-DD] [--window SECONDS] \
  [--format text|json] [--show-orphans]
```

**Arguments**
| Flag | Description |
|------|--------------|
| `--api` | Path to the API log file |
| `--db` | Path to the database log file |
| `--storage` | Path to the storage log file |
| `--date` | Correlation date filter (YYYY-MM-DD) |
| `--window` | Time window in seconds for correlation |
| `--format` | Output format: `text` or `json` |
| `--show-orphans` | Optionally include uncorrelated events |

---

## 📊 Example Output

```
Chain: req_816 (initiated by bob) [09:32:05] API | bob | GET /dashboard/stats
[09:32:06] DB | dashboard_svc | SQL SELECT metric, current_value FROM dashboard_stats
[09:32:08] STORAGE | dashboard_svc | READ cache/dashboard_stats.json (8 KB)
Correlation: HIGH (avg score 1.55)
```

---



## 🧩 Development Notes
```

- Tested with **Python 3.10 – 3.12**
- Works on **Windows**, **macOS**, and **Linux**
- Outputs human-readable text or JSON
- Supports easy containerization via Docker
```
