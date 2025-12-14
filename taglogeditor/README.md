# TagLogEditor

TagLogEditor is a local tool for scanning Imgbrd-Grabber separate tag log `.txt` files, surfacing commonly appearing tags, and quickly removing them (or banning them) in bulk.

## Project layout

```
taglogeditor/
  backend/  # FastAPI service
  frontend/ # React + Vite UI
```

## Quick start

### Backend

```bash
cd taglogeditor/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd taglogeditor/frontend
npm install
npm run dev
```

Open the UI at http://localhost:5173 and point it to the backend running on port 8000.

### Combined run (optional)

From `taglogeditor/frontend` you can also run the backend separately while running the dev server. Add your own process manager or run both commands in separate shells. A convenience script `npm run dev:all` can be added to call `concurrently` if desired.
