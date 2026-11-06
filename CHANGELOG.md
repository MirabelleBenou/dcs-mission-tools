# Changelog

All notable changes to **DCS Mission Tools**. Format based on [Keep a Changelog](https://keepachangelog.com/). Versioning follows [SemVer](https://semver.org/).

## [Unreleased]

### Added
- **Loadout Editor**: an estimated weight for each Mi-24P, Mi-8MTV2, F-4E and Mirage F1EE — empty weight, fuel and stores, gun not counted, detailed on hover — in orange above the recommended maximum, which stays allowed; the *Compose a loadout* window starts from the loadout of the selected aircraft and adds their take-off weight. Empty and maximum weights from the DCS World aircraft definitions.
- **Loadout Editor**: the settings show the values of the selected aircraft — or their range when they differ — and only a changed field is applied; sliders set the fuel as a percentage of the type's maximum and the gun in %, the fields still taking a number.

### Changed
- **Loadout Editor**: a livery can now be applied to aircraft of any country; the summary warns that the DCS mission editor does not offer it for that country, while the game shows it.

## [1.3.0] — 2026-11-05

### Added
- **Loadout Editor**: pick a loadout already in the mission — shown by weapon name — and apply it to every selected aircraft of the same type, players and AI alike; set fuel, flares, chaff and gun in bulk, with the current values and each type's limits shown; apply a livery within the same type and country. Each payload is rewritten whole and verified before the file is offered for download. Weapon names come from pydcs (LGPL-3.0-or-later).
- **Loadout Editor**: compose a loadout station by station, from scratch or from a loadout of the mission, with the weapons each station accepts, mirrored stations and the total weight; a front view of the aircraft for the Mi-24P, Mi-8MTV2, F-4E and Mirage F1EE, the station list for every other type. Front-view drawings by Goldwolf (DCS Reference Guide), used with permission and not covered by the MIT licence; station data from pydcs (LGPL-3.0-or-later).

### Removed
- **Foothold Configurator** is no longer planned: its *Coming soon* tile is gone from the board and from the README.

### Changed
- A *Coming soon* tile now keeps the width of a tool tile instead of stretching across the board.
- **Comm Plan Editor**: channels are numbered as in the cockpit (the Mi-24P's R-863 and R-828 start at channel 0), with the mission file's number in a tooltip; radio names come from a block shared with Mission Plan. The .miz and the template keep the mission file's numbering.
- **Loadout Editor**: one *Apply to selection* button applies the chosen loadout, settings and livery together, under a summary of what will change; the *Compose a loadout* window now keeps the loadout for that button; a livery of another country is dimmed and explained; loadout letters no longer change when the file is saved; the drawing credit sits at the top right of the view.
- **All tools**: every drop-down list opens in the suite's own style instead of the system menu (white on Android), with a search field at the top of any list longer than 15 entries — the aircraft type filter of the Loadout Editor among them; in the Ground Unit Swapper, the Group, Unit and Type filters become such lists and the type pickers share the same look.

## [1.2.1] — 2026-10-16

### Fixed
- **One language across the suite**: switching language on the board or inside any tool now switches the whole suite, open tools included.
- Switching language no longer replaces the loaded file name with "No file loaded".
- Each tool card on the board shows the tool's actual version, read from the tool at build time.

### Changed
- The build script reads `modules/` and writes `dist/dcs_mission_tools.html`, matching the repository layout.

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
