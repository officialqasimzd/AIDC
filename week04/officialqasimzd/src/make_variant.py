"""Generate the per-student copy of the plant shift log.

Every student starts from the same clean simulated plant day. A seed derived
from your student identifier then injects a different set of faults into your
copy, so the evidence you report has to come from your own file.

Student use:

    python src/make_variant.py --student-id your-github-username

Instructor use (prints the injected faults for marking):

    python src/make_variant.py --student-id their-github-username --reveal
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
from datetime import datetime, timedelta
from pathlib import Path

BASE_SEED = 20260112
START = datetime(2026, 1, 12, 6, 0)
HOURS = 24
LINES = ("Line_A", "Line_B", "Line_C")
COLUMNS = [
    "timestamp",
    "line_id",
    "shift",
    "units_produced",
    "downtime_min",
    "energy_kwh",
    "rejected_units",
    "motor_temp_c",
]

# Per-line production character. Identical for every student.
LINE_PROFILE = {
    "Line_A": {"units": (415, 24), "energy": (165.0, 7.0), "temp": (75.0, 1.3), "downtime": (8.0, 4.0), "reject_rate": 0.012},
    "Line_B": {"units": (372, 27), "energy": (152.0, 8.0), "temp": (75.6, 1.5), "downtime": (13.0, 5.0), "reject_rate": 0.026},
    "Line_C": {"units": (404, 22), "energy": (170.0, 6.0), "temp": (74.8, 1.2), "downtime": (9.5, 4.0), "reject_rate": 0.009},
}


def shift_for(moment: datetime) -> str:
    """Course rule: Day covers 06:00-17:59 and Night covers 18:00-05:59."""
    return "Day" if 6 <= moment.hour < 18 else "Night"


def clean_base() -> list[dict]:
    rng = random.Random(BASE_SEED)
    rows: list[dict] = []
    for step in range(HOURS):
        moment = START + timedelta(hours=step)
        for line in LINES:
            profile = LINE_PROFILE[line]
            units = max(300, round(rng.gauss(*profile["units"])))
            downtime = min(45.0, max(1.0, round(rng.gauss(*profile["downtime"]), 1)))
            energy = round(rng.gauss(*profile["energy"]), 1)
            rejects = max(1, round(units * profile["reject_rate"] * rng.uniform(0.5, 1.6)))
            temp = round(rng.gauss(*profile["temp"]), 1)
            rows.append({
                "timestamp": moment.strftime("%Y-%m-%dT%H:%M"),
                "line_id": line,
                "shift": shift_for(moment),
                "units_produced": units,
                "downtime_min": downtime,
                "energy_kwh": energy,
                "rejected_units": rejects,
                "motor_temp_c": temp,
            })
    return rows


def describe(row: dict) -> str:
    return f"{row['line_id']} at {row['timestamp'][-5:]}"


# --- Fault injectors ------------------------------------------------------
# Each injector receives `pick`, which returns a record no other injector has
# touched. Keeping the faults on separate records means a student can find and
# report six distinct problems instead of one tangle.
# Each returns a short description of what it did, for the instructor reveal.

def blank_downtime(rows, rng, pick):
    row = pick()
    row["downtime_min"] = ""
    return f"downtime_min blanked for {describe(row)}"


def blank_energy(rows, rng, pick):
    row = pick()
    row["energy_kwh"] = ""
    return f"energy_kwh blanked for {describe(row)}"


def negative_energy(rows, rng, pick):
    row = pick()
    row["energy_kwh"] = -round(rng.uniform(4.0, 30.0), 1)
    return f"energy_kwh set to {row['energy_kwh']} for {describe(row)}"


def temperature_spike(rows, rng, pick):
    row = pick()
    row["motor_temp_c"] = round(rng.uniform(104.0, 119.0), 1)
    return (f"motor_temp_c set to {row['motor_temp_c']} for {describe(row)} "
            "(judgement case, not a confirmed error)")


def exact_duplicate(rows, rng, pick):
    row = pick()
    rows.append(dict(row))
    return f"exact duplicate of {describe(row)} appended at the end of the file"


def conflicting_key_duplicate(rows, rng, pick):
    row = pick()
    clone = dict(row)
    clone["units_produced"] = int(clone["units_produced"]) + rng.randint(15, 60)
    clone["energy_kwh"] = round(float(clone["energy_kwh"]) + rng.uniform(3.0, 11.0), 1)
    rows.append(clone)
    return f"second record for the {describe(row)} line-hour with different units and energy"


def rejects_exceed_output(rows, rng, pick):
    row = pick()
    row["rejected_units"] = int(row["units_produced"]) + rng.randint(5, 40)
    return f"rejected_units ({row['rejected_units']}) exceeds units_produced for {describe(row)}"


def downtime_out_of_range(rows, rng, pick):
    row = pick()
    row["downtime_min"] = round(rng.uniform(70.0, 140.0), 1)
    return f"downtime_min set to {row['downtime_min']} in a 60-minute period for {describe(row)}"


def unknown_line_id(rows, rng, pick):
    row = pick()
    original = row["line_id"]
    row["line_id"] = rng.choice(["Line_D", original.lower(), original.upper(), original + " "])
    return (f"line_id written as {row['line_id']!r} at {row['timestamp'][-5:]}; "
            "this also leaves that line one hour short of coverage")


def unparseable_timestamp(rows, rng, pick):
    row = pick()
    moment = datetime.strptime(row["timestamp"], "%Y-%m-%dT%H:%M")
    row["timestamp"] = moment.strftime("%d/%m/%Y %H:%M")
    return (f"timestamp rewritten as {row['timestamp']!r} for {row['line_id']}; "
            "this also leaves that line one hour short of coverage")


def shift_mismatch(rows, rng, pick):
    row = pick()
    row["shift"] = "Night" if row["shift"] == "Day" else "Day"
    return f"shift labelled {row['shift']} for {describe(row)}"


def missing_hour(rows, rng, pick):
    row = pick()
    rows.remove(row)
    return f"the {describe(row)} record is absent, leaving a coverage gap"


# One injector is drawn from each group, so every student's file exercises
# every family of check. Which one it is, and which record it lands on,
# differs by student.
FAULT_GROUPS = [
    ("schema", [unknown_line_id, unparseable_timestamp]),
    ("completeness", [blank_downtime, blank_energy]),
    ("uniqueness", [exact_duplicate, conflicting_key_duplicate]),
    ("validity", [negative_energy, rejects_exceed_output, downtime_out_of_range]),
    ("coverage", [missing_hour, shift_mismatch]),
    ("judgement", [temperature_spike]),
]


def slugify(student_id: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", student_id.strip().lower()).strip("-")
    if not slug:
        raise SystemExit("Student id must contain at least one letter or number.")
    return slug


def seed_for(student_id: str) -> int:
    digest = hashlib.sha256(slugify(student_id).encode("utf-8")).hexdigest()
    return int(digest[:12], 16)


def build_variant(student_id: str) -> tuple[list[dict], list[str]]:
    rows = clean_base()
    rng = random.Random(seed_for(student_id))
    taken: set[int] = set()

    def pick() -> dict:
        """Return a record no earlier injector has touched."""
        while True:
            index = rng.randrange(len(rows))
            if index not in taken:
                taken.add(index)
                return rows[index]

    injected: list[str] = []
    for group, injectors in FAULT_GROUPS:
        injector = rng.choice(injectors)
        injected.append(f"[{group}] {injector(rows, rng, pick)}")
    return rows, injected


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--student-id", required=True, help="your GitHub Classroom username")
    parser.add_argument("--out-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--reveal", action="store_true", help="instructor only: print the injected faults")
    args = parser.parse_args()

    slug = slugify(args.student_id)
    rows, injected = build_variant(args.student_id)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    target = args.out_dir / f"shift_log_{slug}.csv"
    with target.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Student id:  {args.student_id}  (slug: {slug})")
    print(f"Written to:  {target.as_posix()}")
    print(f"Rows:        {len(rows)}")
    print(f"SHA-256:     {sha256_of(target)}")
    print()
    print("Copy the path and fingerprint into docs/data_quality_report.md.")
    print("Do not edit this file. Every fault you find must be reported, not repaired.")

    if args.reveal:
        print()
        print("--- INSTRUCTOR REVEAL ---")
        for line in injected:
            print(f"  {line}")
        print(json.dumps({"student_id": args.student_id, "slug": slug, "faults": injected}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
