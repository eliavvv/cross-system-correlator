# Cross-System Event Correlator

A small, usable command-line tool that parses heterogeneous logs (API, DB, storage) and correlates events that belong to the same logical operation. It outputs grouped event chains with a confidence score.

## Quickstart

### Local (Python 3.10+)

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m correlator.cli correlate   --api sample-logs/api.log   --db sample-logs/db.log   --storage sample-logs/storage.log   --date 2025-09-30   --window 60   --format text
```

### Docker

```bash
docker build -t correlator .
docker run --rm -it -v $(pwd)/sample-logs:/app/sample-logs correlator   correlate --api sample-logs/api.log --db sample-logs/db.log --storage sample-logs/storage.log --date 2025-09-30 --window 60 --format text
```

### CLI

```
python -m correlator.cli correlate   --api <path> --db <path> --storage <path>   [--date YYYY-MM-DD] [--window SECONDS] [--format text|json] [--show-orphans]
```
