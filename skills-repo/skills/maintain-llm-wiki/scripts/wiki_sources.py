#!/usr/bin/env python3
"""Record and check direct original-source versions for curated Markdown notes."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile


def within(value, root):
    path = Path(value).expanduser()
    path = (root / path if not path.is_absolute() else path).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path outside {root}: {value}")
    return path


def original(value, vault, wiki):
    path = within(value, vault)
    if path.is_relative_to(wiki) or any(part in {".state", ".llmwiki", ".rag"} for part in path.parts):
        raise ValueError(f"Expected an original source, not wiki or technical state: {value}")
    return path


def frontmatter(text, required=True):
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        if not required:
            return [], text
        raise ValueError("Missing frontmatter")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise ValueError("Unclosed frontmatter")
    return lines[1:end], "".join(lines[end + 1:])


def source_metadata(text):
    header, _ = frontmatter(text)
    reviewed = [line[len("reviewed_at:"):].strip() for line in header if line.startswith("reviewed_at:")]
    if len(reviewed) != 1:
        raise ValueError("Expected one reviewed_at timestamp")
    value = json.loads(reviewed[0])
    if not isinstance(value, str):
        raise ValueError("reviewed_at must be an ISO timestamp string")
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("reviewed_at requires a timezone")
    matches = [line[len("wiki_sources:"):].strip() for line in header if line.startswith("wiki_sources:")]
    if len(matches) != 1:
        raise ValueError("Expected one JSON-valued wiki_sources line")
    sources = json.loads(matches[0])
    if not isinstance(sources, list) or not sources:
        raise ValueError("wiki_sources must be a nonempty list")
    for item in sources:
        if (not isinstance(item, dict) or not isinstance(item.get("path"), str)
                or not item["path"] or not isinstance(item.get("sha256"), str)
                or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"])):
            raise ValueError("Invalid original path or SHA-256")
        if Path(item["path"]).is_absolute():
            raise ValueError("Stored original paths must be vault-relative")
    return sources


def check_page(page, vault, wiki):
    result = {"page": str(page), "status": "unchanged", "sources": [], "errors": []}
    try:
        page = within(page, wiki / "notes")
        if page.suffix != ".md":
            raise ValueError("Curated pages must be Markdown under notes/")
        sources = source_metadata(page.read_text(encoding="utf-8"))
        seen = set()
        for item in sources:
            path = original(vault / item["path"], vault, wiki)
            if path in seen:
                raise ValueError("Duplicate original source")
            seen.add(path)
            actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
            status = "missing" if actual is None else "unchanged" if actual == item["sha256"] else "changed"
            result["sources"].append({"path": str(path.relative_to(vault)), "status": status,
                                      "recorded_sha256": item["sha256"], "actual_sha256": actual})
            if status != "unchanged":
                result["status"] = "review"
    except (OSError, ValueError, TypeError) as error:
        result["status"] = "invalid"
        result["errors"].append(str(error))
    return result


def record(page, values, vault, wiki):
    page = within(page, wiki / "notes")
    if page.suffix != ".md":
        raise ValueError("Curated pages must be Markdown under notes/")
    with page.open(encoding="utf-8", newline="") as stream:
        text = stream.read()
    header, body = frontmatter(text, required=False)
    entries = []
    seen = set()
    for value in values:
        path = original(value, vault, wiki)
        if path not in seen:
            entries.append({"path": str(path.relative_to(vault)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
            seen.add(path)
    if not entries:
        raise ValueError("record requires at least one --source")
    header = [line for line in header if not line.startswith(("wiki_sources:", "reviewed_at:"))]
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    replacement = ("---\n" + "".join(header) + 'reviewed_at: ' + json.dumps(stamp) + "\nwiki_sources: "
                   + json.dumps(entries, ensure_ascii=False, separators=(",", ":")) + "\n---\n" + body)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=page.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(replacement)
        temporary.chmod(page.stat().st_mode & 0o777)
        os.replace(temporary, page)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return {"ok": True, "page": str(page), "reviewed_at": stamp, "sources": entries}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check", "record"])
    parser.add_argument("--vault", required=True, type=Path)
    parser.add_argument("--wiki", required=True, type=Path)
    parser.add_argument("--page", action="append", default=[])
    parser.add_argument("--source", action="append", default=[])
    args = parser.parse_args()
    vault = args.vault.expanduser().resolve()
    wiki = within(args.wiki, vault)
    if not vault.is_dir() or not wiki.is_dir() or not (wiki / "notes").is_dir():
        raise ValueError("Expected existing vault, wiki and notes/ directories")
    if args.command == "record":
        if len(args.page) != 1:
            raise ValueError("record requires exactly one --page")
        print(json.dumps(record(wiki / args.page[0], args.source, vault, wiki), ensure_ascii=False, indent=2))
        return 0
    if args.source:
        raise ValueError("--source is for record only")
    pages = [wiki / p for p in args.page] if args.page else sorted((wiki / "notes").rglob("*.md"))
    results = [check_page(p, vault, wiki) for p in pages]
    ok = all(p["status"] == "unchanged" for p in results)
    print(json.dumps({"ok": ok, "pages": results}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "pages": [], "errors": [str(error)]}, ensure_ascii=False))
        sys.exit(1)
