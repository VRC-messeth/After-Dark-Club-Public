#!/usr/bin/env python3
"""Mirror Rolling-Ads/<owner>[-NN].png into fixed slot files the world can bake.

WHY: a VRChat world cannot build a URL at runtime -- every URL it fetches is saved
into the scene at upload. The bot names ads after the uploader
(`usr_<id>.png`, `usr_<id>-NN.png`), which no world could know in advance. So the
world bakes SLOT_COUNT fixed URLs (`Rolling-Ads/slots/ad_000.png` ...) and this
script keeps those files and `slots/manifest.json` in step with the bot's folder.
A new ad goes live at the next join, with no world upload. (Same pattern as the
After-Dark-Reels repo.)

Rules:
  * an ad keeps its slot while it exists (its file is overwritten on change);
  * a removed ad's slot file is deleted and the slot freed;
  * a new ad takes the free slot that was freed LONGEST ago (never-used first),
    so a just-freed URL -- still in GitHub Pages' ~10 min cache -- is not
    immediately handed to somebody else's art;
  * manifest order interleaves owners (everyone's 1st ad, then everyone's 2nd ...)
    so a world that can only hold a few images still shows many different people.

Idempotent: running it twice changes nothing the second time.
"""
import json
import os
import re
import sys
import time

SLOT_COUNT = 128          # MUST match AdcBuildRollingAds.SlotCount in the world
ADS_DIR = "Rolling-Ads"
SLOT_DIR = os.path.join(ADS_DIR, "slots")
MANIFEST = os.path.join(SLOT_DIR, "manifest.json")
EXTS = (".png", ".jpg", ".jpeg")
NUMBERED = re.compile(r"^(?P<owner>.+)-(?P<n>\d\d)$")


def slot_name(i):
    return "ad_%03d.png" % i


def owner_and_index(file_name):
    stem = os.path.splitext(file_name)[0]
    m = NUMBERED.match(stem)
    if m:
        return m.group("owner"), int(m.group("n"))
    return stem, 1


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def write_bytes(path, data):
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)


def main(root):
    os.chdir(root)
    os.makedirs(SLOT_DIR, exist_ok=True)

    sources = sorted(
        f for f in os.listdir(ADS_DIR)
        if os.path.isfile(os.path.join(ADS_DIR, f)) and f.lower().endswith(EXTS)
    )

    old = {}
    if os.path.isfile(MANIFEST):
        try:
            with open(MANIFEST, encoding="utf-8") as f:
                old = json.load(f)
        except ValueError:
            print("manifest unreadable -- rebuilding slot map from scratch")
            old = {}

    # file -> slot, from the previous run
    assigned = {}
    for e in old.get("ads", []):
        s, f = e.get("slot"), e.get("file")
        if isinstance(s, int) and 0 <= s < SLOT_COUNT and f and f not in assigned:
            assigned[f] = s
    freed_at = {int(k): v for k, v in old.get("freedAt", {}).items()}

    now = int(time.time())
    changes = []

    # 1. free the slots of ads that are gone
    for f, s in list(assigned.items()):
        if f not in sources:
            del assigned[f]
            freed_at[s] = now
            p = os.path.join(SLOT_DIR, slot_name(s))
            if os.path.exists(p):
                os.remove(p)
            changes.append("freed slot %d (%s removed)" % (s, f))

    # 2. place new ads
    used = set(assigned.values())
    for f in sources:
        if f in assigned:
            continue
        free = [s for s in range(SLOT_COUNT) if s not in used]
        if not free:
            print("WARNING: all %d slots are taken; %s is NOT shown" % (SLOT_COUNT, f))
            continue
        s = min(free, key=lambda i: (freed_at.get(i, 0), i))
        assigned[f] = s
        used.add(s)
        freed_at.pop(s, None)
        changes.append("slot %d <- %s" % (s, f))

    # 3. make every slot file match its source byte for byte
    for f, s in assigned.items():
        src = read_bytes(os.path.join(ADS_DIR, f))
        dst_path = os.path.join(SLOT_DIR, slot_name(s))
        if not os.path.exists(dst_path) or read_bytes(dst_path) != src:
            write_bytes(dst_path, src)
            changes.append("slot %d updated from %s" % (s, f))

    # 4. stray slot files (hand edits, an older run) are removed
    keep = {slot_name(s) for s in assigned.values()} | {"manifest.json"}
    for f in os.listdir(SLOT_DIR):
        if f not in keep:
            os.remove(os.path.join(SLOT_DIR, f))
            changes.append("removed stray %s" % f)

    # 5. manifest, owners interleaved
    by_owner = {}
    for f, s in assigned.items():
        o, n = owner_and_index(f)
        by_owner.setdefault(o, []).append((n, f, s))
    rounds = []
    for o in sorted(by_owner):
        for k, (n, f, s) in enumerate(sorted(by_owner[o])):
            rounds.append((k, o, s, f))
    rounds.sort()
    ads = [{"slot": s, "owner": o, "file": f} for (k, o, s, f) in rounds]

    manifest = {
        "version": 1,
        "slotCount": SLOT_COUNT,
        "base": "https://vrc-messeth.github.io/After-Dark-Club-Public/Rolling-Ads/slots/",
        "ads": ads,
        "freedAt": {str(k): v for k, v in sorted(freed_at.items())},
    }
    text = json.dumps(manifest, indent=1, ensure_ascii=False) + "\n"
    prev = None
    if os.path.isfile(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as f:
            prev = f.read()
    if text != prev:
        with open(MANIFEST, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        changes.append("manifest: %d ad(s)" % len(ads))

    for c in changes:
        print(c)
    print("%d ad(s) in %d slot(s); %d change(s)" % (len(ads), SLOT_COUNT, len(changes)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
