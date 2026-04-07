# Enterprise DBA Agent (OpenEnv)

This environment simulates a production NoSQL database. An AI agent acts as a Database Administrator (DBA) to optimize schemas, manage server RAM, and ensure data safety.

## Action Space
- `create_snapshot`: Takes a backup.
- `drop_collection`: Deletes a table.
- `create_index`: Adds an index for speed.
- `drop_index`: Frees up RAM.
- `create_compound_index`: Complex indexing.

## Tasks
1. **Easy (Safe Cleanup):** Drop useless logs, but ONLY after taking a snapshot.
2. **Medium (N+1 Query Fix):** Create an index on `email` to fix a slow COLLSCAN query.
3. **Hard (Concurrency & RAM):** Drop an old index to free up RAM, then safely create a compound index without crashing the server (OOM).

## Setup & Run Locally
1. Install dependencies: `pip install -r requirements.txt`
2. Start the server: `uvicorn environment:app --host 0.0.0.0 --port 8000`
3. Test the baseline: `python inference.py`