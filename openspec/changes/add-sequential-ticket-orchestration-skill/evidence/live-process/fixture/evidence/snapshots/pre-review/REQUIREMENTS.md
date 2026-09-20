# Ticket export requirements

The public interface is `python3 ticket_export.py <input.json> --format csv|json [--status todo|done]`.

R1. Input is a JSON array of objects with positive integer id, string title and status. Preserve ids; trim surrounding title whitespace. Status values use todo or done, ignoring case and surrounding whitespace. Normalize output status to lowercase. Input validation outside these documented valid inputs is out of scope.
R2. Without a status filter, export every input item sorted by numeric id. With --status, export only items matching the normalized status. Both formats must yield the same selected values and ordering, including normalized input statuses.
R3. CSV uses the header id,title,status and standard CSV quoting so commas, quotes and line breaks survive a CSV-reader round trip. JSON is an array containing those same three fields. Empty results have a CSV header only or an empty JSON array.
R4. Reading input and producing output must not change the input file. No network, external dependencies or extra business fields are needed.
