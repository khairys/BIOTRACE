"""R-AUD-03 canonical, spreadsheet-safe UTF-8 exports [MVP]."""

import csv
import io
import json

from pydantic import BaseModel


def artifact_name(stem: str, extension: str, simulated: bool) -> str:
    return f"{stem}{'_SIMULASI' if simulated else ''}.{extension}"


def canonical_csv(rows: list[BaseModel], fields: list[str] | None = None) -> bytes:
    """R-AUD-03: sorted columns/rows, two decimals, LF; neutralize CSV formula cells."""
    records = [r.model_dump(mode="json") for r in rows]
    if fields is None:
        fields = sorted(records[0]) if records else []
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in records:
        formatted = {}
        for key in fields:
            value = row.get(key)
            if value is None:
                value = ""
            elif isinstance(value, bool):
                value = str(value).lower()
            elif isinstance(value, float):
                value = f"{value:.2f}"
            elif isinstance(value, list):
                value = ";".join(
                    f"{x['species']}:{x['pct']:.2f}"
                    if isinstance(x, dict) and "species" in x
                    else str(x)
                    for x in value
                )
            elif isinstance(value, dict):
                value = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            if isinstance(value, str) and value.startswith(("=", "+", "-", "@", "\t", "\r")):
                value = "'" + value
            formatted[key] = value
        writer.writerow(formatted)
    return output.getvalue().encode("utf-8")
