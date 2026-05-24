# DCS Mission Tools

A collection of single-file HTML tools for **DCS World** mission preparation — built for squadron leaders and mission designers who want to get more done before engine start.

> **Offline-first. No install. No server. Open the file, work, save.**

---

## Tools

### [Ground Unit Swapper](./dcs_ground_unit_swapper_v1_3_0.html) `v1.3.0`

Bulk-edit ground unit types and skills in a `.miz` file without touching the Mission Editor.

- Load a `.miz` → see every ground vehicle in a filterable table
- Filter by coalition, family, group, unit, or free text
- Multi-select rows → replace type and/or skill in one click
- Surgical patch — only modified values are rewritten; scripts (CTLD, MOOSE…) are untouched
- Export/import edits as JSON for reuse across missions

---

### [Comm Plan Editor](./dcs_comm_plan_editor_v1_0_0.html) `v1.0.0`

Edit radio frequencies for all Client slots in a `.miz` without opening the Mission Editor.

- Full visibility of every frequency, radio, and channel per aircraft type
- Edit frequencies inline, chain multiple save cycles without reloading
- Export/import frequency templates (`dcs-comm-plan-template-v1`) to standardize comms across missions
- Retokenize safety check — a corrupt `.miz` is never written to disk

---

## Usage

1. Download the HTML file for the tool you need (Directly from the repo)
2. Open it in Chrome or Firefox — no web server required
3. Drag & drop your `.miz` file onto the drop zone
4. Edit, then click **Save** — a new `.miz` is downloaded, the original is never overwritten

Both tools work fully offline after the first load (CDN dependency: JSZip via cdnjs).

---

## Design

All tools share a common visual language: dark cockpit background, monospace accents, per-tool identification color. Details in [`DESIGN_DCS_Mission_Suite.md`](./DESIGN_DCS_Mission_Suite.md) (for contributors and future tool authors).

---

## Compatibility

| Browser | Status |
|---------|--------|
| Chrome / Chromium | ✅ Recommended |
| Firefox | ✅ Supported |
| Edge | ✅ Supported |
| Safari | ⚠️ Not tested |

DCS World versions tested: **2.9.x** — any version that produces standard `.miz` (ZIP + Lua) files should work.

---

## Related

- **[DCS World Briefing Generator](https://github.com/MirabelleBenou/dcs-briefing-generator)** — military-style mission briefing documents (separate repo)

---

## License

MIT — see [LICENSE](./LICENSE)

---

*Built by [4th VEAW](https://github.com/MirabelleBenou) — 4th VEAW / KHR-26 / Mi-24P*
