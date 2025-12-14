# TagLogEditor Backend

FastAPI service for scanning and updating Imgbrd-Grabber log files.

## Setup

```bash
cd taglogeditor/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing

```bash
pytest
```
