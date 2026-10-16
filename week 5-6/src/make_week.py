"""Generate a week of hourly plant data for one student.

Week 3 gave you one day. Baselines need more than that: "same hour yesterday"
has nothing to copy on day one, and a regression fitted on 24 rows per line
learns the noise. This produces seven days, three lines, one row per line per
hour, in exactly the Week 3 columns plus one extra.

The extra column is deliberate. One of the columns in this file will not exist
at the top of the hour when the prediction has to be made. Finding it is Part
C of the lab, so it is not named here.

Usage:

    python src/make_week.py --student-id your-github-username

The file lands in data/raw/, and the SHA-256 is printed so you can record it,
as you did in Week 3. The same username always produces the same file.
"""

from __future__ import annotations

import argparse
import hashlib
import math
import random
from datetime import datetime, timedelta

from paths import DATA_RAW

BASE_SEED = 20260112
START = datetime(2026, 1, 12, 6, 0)
DAYS = 7
HOURS = 24 * DAYS
LINES = ("Line_A", "Line_B", "Line_C")
COLUMNS = [
    "timestamp", "line_id", "shift", "units_produced", "downtime_min",
    "energy_kwh", "rejected_units", "motor_temp_c", "energy_kwh_smoothed",
]

# Same per-line character as Weeks 1 to 4, so the lines feel familiar.
LINE_PROFILE = {
    "Line_A": {"units": (415, 24), "energy": 165.0, "temp": (75.0, 1.3), "downtime": (8.0, 4.0), "reject_rate": 0.012},
    "Line_B": {"units": (372, 27), "energy": 152.0, "temp": (75.6, 1.5), "downtime": (13.0, 5.0), "reject_rate": 0.026},
    "Line_C": {"units": (404, 22), "energy": 170.0, "temp": (74.8, 1.2), "downtime": (9.5, 4.0), "reject_rate": 0.009},
}

# Energy has structure a model can find: it follows units produced, it dips at
# night, and it carries over from one hour to the next. None of this is stated
# in the README; discovering how much of it each baseline captures is the lab.
KWH_PER_UNIT = 0.12
NIGHT_DIP_KWH = 10.0
CARRY_OVER = 0.7
NOISE_KWH = 3.0


def shift_for(moment: datetime) -> str:
    """Course rule: Day covers 06:00-17:59 and Night covers 18:00-05:59."""
    return "Day" if 6 <= moment.hour < 18 else "Night"


def seed_for(student_id: str) -> int:
    digest = hashlib.sha256(student_id.strip().lower().encode("utf-8")).hexdigest()
    return BASE_SEED + int(digest[:8], 16)


def generate(student_id: str) -> list[dict]:
    rng = random.Random(seed_for(student_id))
    rows: list[dict] = []
    previous_shock = {line: 0.0 for line in LINES}

    # One hour in the week where a motor ran hot and drew extra energy. Every
    # baseline will miss it, and the student already knows who to ask about it.
    # Steps 146 to 160 fall in daylight on the last full day, which the lab
    # holds out as test data, so the spike is scored rather than trained on.
    spike_step = rng.randint(146, 160)
    spike_line = rng.choice(LINES)

    for step in range(HOURS):
        moment = START + timedelta(hours=step)
        night = shift_for(moment) == "Night"
        for line in LINES:
            p = LINE_PROFILE[line]
            units = max(300, round(rng.gauss(*p["units"]) - (18 if night else 0)))
            downtime = min(45.0, max(1.0, round(rng.gauss(*p["downtime"]), 1)))
            shock = CARRY_OVER * previous_shock[line] + rng.gauss(0, NOISE_KWH)
            energy = (p["energy"] + KWH_PER_UNIT * (units - 400)
                      - (NIGHT_DIP_KWH if night else 0.0) + shock)
            temp = rng.gauss(*p["temp"])
            if step == spike_step and line == spike_line:
                temp = 112.0
                energy += 38.0
            previous_shock[line] = shock
            rejects = max(1, round(units * p["reject_rate"] * rng.uniform(0.5, 1.6)))
            rows.append({
                "timestamp": moment.strftime("%Y-%m-%dT%H:%M"),
                "line_id": line,
                "shift": shift_for(moment),
                "units_produced": units,
                "downtime_min": downtime,
                "energy_kwh": round(energy, 1),
                "rejected_units": rejects,
                "motor_temp_c": round(temp, 1),
            })

    # The extra column: a centred two-hour smoothing of energy, the kind of
    # tidied series a reporting export often carries. A centred average of
    # this hour and the next contains the next hour, which has not happened
    # when the prediction is made.
    by_line: dict[str, list[dict]] = {}
    for r in rows:
        by_line.setdefault(r["line_id"], []).append(r)
    for seq in by_line.values():
        for i, r in enumerate(seq):
            nxt = seq[i + 1]["energy_kwh"] if i + 1 < len(seq) else r["energy_kwh"]
            r["energy_kwh_smoothed"] = round((r["energy_kwh"] + nxt) / 2.0, 1)
    return rows


def write_csv(rows: list[dict], path) -> str:
    lines = [",".join(COLUMNS)]
    for r in rows:
        lines.append(",".join(str(r[c]) for c in COLUMNS))
    text = "\n".join(lines) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--student-id", required=True,
                        help="your GitHub username; the same id always gives the same file")
    args = parser.parse_args(argv)
    student = args.student_id.strip().lower()
    if not student or "/" in student or "\\" in student:
        parser.error("student id must be a plain username")

    rows = generate(student)
    out = DATA_RAW / f"shift_week_{student}.csv"
    digest = write_csv(rows, out)
    print(f"Wrote {out}")
    print(f"Rows: {len(rows)} ({DAYS} days, {len(LINES)} lines, hourly)")
    print(f"SHA-256: {digest}")
    print("Record the fingerprint in docs/interpretation_note.md before you do anything else.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
