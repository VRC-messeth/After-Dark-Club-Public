# After Dark Club - Public

Public data for the **After Dark Club** VRChat world. The world downloads these files at
runtime (VRCStringDownloader) to know who gets which icon above their head: the group owner,
the moderators, and in future other roles such as Patreon supporters.

There is no code here and nothing secret. Everything in this repo is already visible on
VRChat (group membership, display names, user ids).

## Layout

```
Groups/
  <GroupName>-<grp_id>/
    roles.json
```

One folder per VRChat group, named `<group name with spaces as underscores>-<group id>`, so a
folder is self-describing and the id is unambiguous. Today there is one group:

| Group | Folder |
|---|---|
| After Dark | `Groups/After_Dark-grp_a9da0233-adaa-48c8-b2cb-ae0326514929/` |

## `roles.json`

Raw URL the world loads:

```
https://raw.githubusercontent.com/VRC-messeth/After-Dark-Club-Public/main/Groups/After_Dark-grp_a9da0233-adaa-48c8-b2cb-ae0326514929/roles.json
```

Schema version 1:

```json
{
  "schemaVersion": 1,
  "generatedAtUtc": "2026-09-03T12:00:00Z",
  "group":         { "id": "grp_...", "name": "After Dark" },
  "sourceGroupId": "grp_...",
  "roles":         ["REX", "MOD"],
  "members": [
    { "displayName": "messeth", "userId": "usr_...", "roles": ["REX"] },
    { "displayName": "Slide ®", "userId": "usr_...", "roles": ["MOD"] }
  ]
}
```

| Field | Meaning |
|---|---|
| `group` | The group this roster belongs to. |
| `sourceGroupId` | The group whose membership was scanned to produce it (the mod group). |
| `roles` | Every role key that can appear in `members[].roles`, in display priority order. |
| `members[].displayName` | **The key the world matches on.** Udon can read a player's display name but not their user id. Exact, case-sensitive match. |
| `members[].userId` | Informational. |
| `members[].roles` | `REX` = the group owner. `MOD` = every other member of the mod group, whatever their VRChat group role is called. |

Consumers should ignore unknown role keys and any `schemaVersion` they do not understand, so new
roles can be added without breaking the world.

## How it is updated

**Do not edit `roles.json` by hand.** The After Dark Manager desktop app regenerates it every
time it starts: it lists the current members of the mod group, refreshes their display names,
and commits the file here only when the roster actually changed. A manual edit survives until
the next start at most.

`raw.githubusercontent.com` is cached for around five minutes, so a change can take that long to
reach a running instance.
