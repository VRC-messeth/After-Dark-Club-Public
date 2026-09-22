"""Owner-only, idempotent transition of one pending medal season to released."""
import argparse
import json
import os
from pathlib import Path
import time

OWNER = "vrc-messeth"
SEASON = "medals-2026-09"
MIN_UTC = 1789603200


def launch_record(record, actor, expected_season, now):
    if actor.lower() != OWNER:
        raise ValueError("Only the world owner may launch medals")
    if expected_season != SEASON or record.get("seasonId") != SEASON:
        raise ValueError("Season does not match this release")
    if type(record.get("schemaVersion")) is not int or record["schemaVersion"] != 1:
        raise ValueError("Invalid schema")
    start = record.get("startsUtc")
    if type(start) is not int or start < 0 or (start != 0 and start < MIN_UTC):
        raise ValueError("Invalid start timestamp; refusing to replace it")
    if start:
        return dict(record), False
    if type(now) is not int or now < MIN_UTC:
        raise ValueError("Invalid launch clock")
    result = dict(record)
    result["startsUtc"] = now
    return result, True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--season", required=True)
    args = parser.parse_args()
    path = Path(args.file)
    record = json.loads(path.read_text(encoding="utf-8"))
    result, changed = launch_record(record, os.environ.get("GITHUB_ACTOR", ""), args.season, int(time.time()))
    if changed:
        path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("Season launched" if changed else "Already launched; timestamp preserved")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as out:
            out.write(f"Medal season `{SEASON}`: start `{result['startsUtc']}` UTC Unix seconds. "
                      "Repeated runs preserve this timestamp. Pages propagation may take several minutes.\n")


if __name__ == "__main__":
    main()

