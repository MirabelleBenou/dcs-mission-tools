# DCS Mission Tools

A web-based toolset to prepare and edit **DCS World** missions (`.miz` files), built for the **4th VEAW** virtual air wing.

**Version: 1.2.0** · License: MIT

---

## What it is

A **single HTML file** (`dcs_mission_tools.html`) hosting three mission editors. Everything runs **in the browser, locally**: no server, no file upload, no connection required. Open the page, drop a `.miz`, edit, save — the `.miz` never leaves your machine.

### The three tools

| Tool | Purpose |
|---|---|
| **Comm Plan Editor** (`C·P`) | Edit the communications plan (radio frequencies / presets). |
| **Ground Unit Swapper** (`G·U`) | Bulk-swap ground unit types and skill, with filters by coalition / group / type / family (Armor, Artillery, AirDef, Radar/EWR, Unarmed, Infantry). |
| **Weather Editor** (`W·X`) | Edit weather: date/time, wind (3 layers), clouds and precipitation, 34 presets. |

### Highlights

- **100% local & offline** — JSZip is bundled in; nothing is uploaded.
- **Shared working file** — the same `.miz` flows from one tool to the next; edits accumulate until you save.
- **Strict preservation** — critical data left intact (groups/units are read-only so CTLD/MOOSE scripts don't break; the `.miz`'s companion files are kept).
- **Bilingual EN / FR** — toggle via a flag, choice is remembered.
- **Surgical patching** — the `.miz` is edited in place, without a full rewrite.

---

## Usage

1. Download `dcs_mission_tools.html`.
2. Open it in a recent browser (Chrome, Edge, Firefox, Brave…).
3. Pick a tool, drop a `.miz` file, edit.
4. **Save**: a new `.miz` is downloaded (your original is left untouched).

> Tip: always keep a backup of your missions before editing.

---

## For developers (build)

The page is **built**, not hand-written: `build_mission_tools.py` reads the module sources and tiles, base64-encodes them, and produces the single file.

```
mission-tools-edition/
  build_mission_tools.py     # shell + bundler
  modules/  dcs_comm_plan_editor.html  dcs_ground_unit_swapper.html  dcs_weather_editor.html
  tiles/    cp.webp  gu.webp  wx.webp
  dist/     dcs_mission_tools.html
```

Rules: the **source of truth** is the standalone module (never the built file); filenames carry **no version** (versioning lives in GitHub tags/releases).

---

## About

Made by and for the **4th VEAW** community (veaw4.fr). A companion to the **DCS Briefing Generator** (mission briefing generation).

Feedback and suggestions are welcome via GitHub issues.
