import argparse
import csv
import io
import json
from pathlib import Path


def export_csv(tickets, status):
    rows = []
    for ticket in tickets:
        if status is None or ticket["status"].strip().lower() == status:
            rows.append({"id": ticket["id"], "title": ticket["title"].strip(), "status": ticket["status"].strip().lower()})
    rows.sort(key=lambda row: row["id"])
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=["id", "title", "status"])
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def export_json(tickets, status):
    rows = []
    for ticket in tickets:
        if status is None or ticket["status"].strip().lower() == status:
            rows.append({"id": ticket["id"], "title": ticket["title"].strip(), "status": ticket["status"].strip().lower()})
    rows.sort(key=lambda row: row["id"])
    return json.dumps(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--format", choices=["csv", "json"], required=True)
    parser.add_argument("--status", choices=["todo", "done"])
    args = parser.parse_args()
    tickets = json.loads(args.input.read_text())
    output = export_csv(tickets, args.status) if args.format == "csv" else export_json(tickets, args.status)
    print(output, end="" if args.format == "csv" else "\n")


if __name__ == "__main__":
    main()
