"""
File Search service.

Scans the configured workspace directory (FILE_SEARCH_WORKSPACE_DIR), filtering
for PDF, image, and TXT files, and indexes filenames + plain-text contents for
simple substring search. Re-scans on every search call (the workspace is
expected to be small/local — a personal assistant's file area, not a corpus).
"""
import os

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".png", ".jpg", ".jpeg", ".gif", ".webp"}
TEXT_EXTENSIONS = {".txt"}


def _index_workspace(workspace_dir: str) -> list[dict]:
    entries = []
    if not os.path.isdir(workspace_dir):
        return entries

    for root, _dirs, files in os.walk(workspace_dir):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                continue
            full_path = os.path.join(root, fname)
            content_snippet = ""
            if ext in TEXT_EXTENSIONS:
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content_snippet = f.read(2000)
                except OSError:
                    content_snippet = ""
            entries.append(
                {
                    "filename": fname,
                    "path": full_path,
                    "extension": ext,
                    "size_bytes": os.path.getsize(full_path),
                    "content_snippet": content_snippet,
                }
            )
    return entries


def search_files(workspace_dir: str, query: str) -> list[dict]:
    query_lower = query.lower().strip()
    index = _index_workspace(workspace_dir)
    if not query_lower:
        return index

    results = []
    for entry in index:
        if query_lower in entry["filename"].lower() or query_lower in entry["content_snippet"].lower():
            results.append(entry)
    return results
