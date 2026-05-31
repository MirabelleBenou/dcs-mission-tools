# Changelog

All notable changes to **DCS Mission Tools**. Format based on [Keep a Changelog](https://keepachangelog.com/). Versioning follows [SemVer](https://semver.org/).

## [1.2.0] — 2026-05-30

First **unified** release of the suite: the three tools and the shell are aligned on a single version.

### Added
- Single-file suite `dcs_mission_tools.html` bundling Comm Plan Editor, Ground Unit Swapper and Weather Editor in isolated iframes.
- **Shared working file**: a `.miz` flows between tools, edits accumulate until you save.
- JSZip **bundled** into each tool → fully offline.

### Changed
- **Ground Unit Swapper**: families regrouped (**AirDef** = SAM + AAA, **Unarmed** = Logistics + Infra/C2); condensed filters; denser table (current type on one line, *new type* and *skill* aligned).
- Chassis homogenized across the three tools (layout, header, saving, internationalization).

### Fixed
- Saving now produces a clean `.miz` (no more `.miz.zip`); consistent extension check.
- Action bar stays anchored at the bottom, both standalone and embedded.
- Landing page scrolling restored on mobile.
- "Unsaved changes" warning working across all three tools.

---

> Per-tool version numbers from before are consolidated starting with this `1.2.0` release.

[1.2.0]: https://github.com/MirabelleBenou/dcs-briefing-generator/releases
