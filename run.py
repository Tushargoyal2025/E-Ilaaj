"""
Run the E-Ilaaj dev server.

Use this instead of the `uvicorn` CLI command — it excludes the database
and vector-store files from the auto-reload watcher, so the server doesn't
restart every time a chat message gets saved.

Usage:
    python run.py
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        # Only restart the server when a .py file changes — this is an
        # allowlist, so database writes, chroma_db updates, or any other
        # file changes (present or future) will never trigger a restart.
        reload_includes=["*.py"],
    )
