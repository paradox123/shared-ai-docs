import argparse
import csv
import io
import json
from pathlib import Path


def prepare_rows(tickets, status):
    rows = []
    for ticket in tickets:
        normalized_status = ticket["status"].strip().lower()
        if status is None or normalized_status == status:
            rows.append({"id": ticket["id"], "title": ticket["title"].strip(), "status": normalized_status})
    rows.sort(key=lambda row: row["id"])
    return rows


def export_csv(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=["id", "title", "status"])
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--format", choices=["csv", "json"], required=True)
    parser.add_argument("--status", choices=["todo", "done"])
    args = parser.parse_args()
    tickets = json.loads(args.input.read_text())
    rows = prepare_rows(tickets, args.status)
    output = export_csv(rows) if args.format == "csv" else json.dumps(rows)
    print(output, end="" if args.format == "csv" else "\n")


if __name__ == "__main__":
    main()
