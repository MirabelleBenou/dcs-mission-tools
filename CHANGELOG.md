# Changelog

All notable changes to **DCS Mission Tools**. Format based on [Keep a Changelog](https://keepachangelog.com/). Versioning follows [SemVer](https://semver.org/).

## [Unreleased]

### Added
- **Loadout Editor**: the front view now covers 45 aircraft types — every aircraft of Goldwolf's DCS Reference Guide that the editor knows: A-10A/C, AH-64D, AJS37, AV-8B, C-101CC, C-130J, F-100D, F-14A/B, F-15C, F-15E, F-16C, F-5E, F-86F, F/A-18C, J-11A, JF-17, Ka-50, L-39ZA, M-2000C, MB-339, MiG-15, MiG-19, MiG-21, MiG-29, Mirage F1, OH-58D, SA342, Su-25, Su-25T, Su-27, Su-33 and UH-1H, besides the Mi-24P, Mi-8MT, F-4E and Mirage F1EE; mirrored stations follow the drawing.
- **Loadout Editor**: the *Compose a loadout* window now refuses loadouts the aircraft cannot use. It follows the station rules that the DCS World mission editor applies to 32 aircraft types (A-10, AV-8B, F-14, F-15E, F-4E, M-2000C, Mi-24P, MiG-21bis, MiG-29 and others): a clashing weapon is greyed out with the station it clashes with, and a weapon that needs another one — the same missile under the other wing of the M-2000C, for instance — says what to fit and where (*Symmetric* fits it for you). Three rules from the manuals are kept on top: on the AJS37, one air-to-ground weapon at a time (the AKAN gun pod goes with the RB 75 or the RB 05, Sidewinders with anything); on the MiG-21bis, the SPS-141 pod or the ASO-2 dispenser, not both; on the Mirage F1, R530 missiles under the fuselage or under the wings, not both. A loadout from the mission that breaks a rule is flagged and cannot be kept until fixed. Rules read from the DCS World aircraft definitions, the official manuals, Chuck's guides and Goldwolf's DCS Reference Guide.
- **Loadout Editor**: change the country of a group within its side — to a country that already has units in the mission or to another country of the side. The whole group moves (an unchecked aircraft goes with its group); a country that does not fly the aircraft type is greyed out; the callsign is rewritten when the new country writes it differently (a name such as Enfield 1-1, or a number), as the DCS mission editor would. Country and aircraft lists from DCS World (`db_countries.lua`) and pydcs.
- **Loadout Editor**: a group can now move to a country of another side — the country list shows every side, current side first, and the callsign follows the new country. The summary warns, without blocking, when a group departs from an airfield, ship or FARP of its former side, is targeted by another group's task, has tasks against groups, or is named in triggers. Airfield names from pydcs.

### Changed
- **All tools**: messages now look and behave the same across the suite — they appear bottom right, just above the bottom bar so they never hide *Save*, marked ✅ ⚠️ ❌ by kind, errors staying 6 s; confirmations open in the suite's own window (Cancel, Escape or a tap outside to back out) instead of the browser's dialog; every tool shows the same loading spinner while a mission is read, and the Weather Editor's custom-weather notice moves under the header, like the Ground Unit Swapper's.
- **All tools**: messages say what happened in plain words — an unreadable file, a failed save or a wrong comm plan each get one clear sentence instead of a technical error; the Comm Plan Editor and the Weather Editor confirm a loaded mission like the other tools; the home screen refuses a file that is not a mission before keeping it, and leaving a tool says what happens to unsaved changes; every drop zone reads the same, and the Loadout Editor gets its own icon.
- **All tools**: one folding sign across the suite — a triangle in the tool's colour, left of the title, that turns when open — and the whole header folds, with larger touch targets; the Comm Plan Editor and the Ground Unit Swapper move their two rare actions into a menu, which keeps their bottom bar to two rows on a phone; the Ground Unit Swapper's filters fold away (folded by default on a phone, with a count of active filters) and its banner becomes a one-line hint, giving the table twice the height on a phone; the drop screen fits a phone held sideways; on the home screen, messages no longer hide the working-file bar.
- **All tools**: finishing touches — Roboto Mono is now embedded, so numbers look the same on every machine; the language button and the back button are full-size touch targets; the Ground Unit Swapper is olive again (it borrowed the Comm Plan Editor's amber); the Comm Plan Editor's filters look like the other tools'; labels, counters and saved-file names read the same in all four tools; clearing every change in the Comm Plan Editor, or loading another mission with unsaved changes in the other tools, now asks first.

### Fixed
- **All tools**: reopening a tool with unsaved changes after the working file has changed — saved in another tool, or another mission picked on the home screen — now asks whether to reload it or keep your changes, instead of erasing them; a mission picked again under the same name is read again; the Ground Unit Swapper, once saved, starts from the saved file like the other tools; its type cell can be opened from the keyboard.
- **Ground Unit Swapper**: unit names such as the ZSU-23-4 Shilka's "Gun Dish" no longer show stray backslashes.
- **Loadout Editor**: the F-5E front view is drawn in the theme's colour like the others, and the MiG-21bis attachment points sit on their pylons.
- **All tools**: the check made after writing a mission now reads it with Lua's own table grammar, so a missing separator between two fields stops the save instead of passing unnoticed, and a mission with such a defect is refused when opened. The Loadout Editor's country and side change now writes missions saved by pydcs and the generators built on it, which leave no comma after the last field of a table, correctly.

## [1.4.0] — 2026-11-08

### Added
- **Loadout Editor**: an estimated weight for each Mi-24P, Mi-8MTV2, F-4E and Mirage F1EE — empty weight, fuel and stores, gun not counted, detailed on hover — in orange above the recommended maximum, which stays allowed; the *Compose a loadout* window starts from the loadout of the selected aircraft and adds their take-off weight. Empty and maximum weights from the DCS World aircraft definitions.
- **Loadout Editor**: the settings show the values of the selected aircraft — or their range when they differ — and only a changed field is applied; sliders set the fuel as a percentage of the type's maximum and the gun in %, the fields still taking a number.
- **Comm Plan Editor**: each radio shows its frequency band under its name; a frequency typed outside the band is refused with the band quoted, one already in the mission is shown in orange without blocking the save, and an imported template value outside the band is skipped. Bands from the DCS World mission editor, cross-checked with Chuck's Guide for the Mi-24P; Mi-8MTV2 from Chuck's Guide, Mirage F1EE from the Aerges manual; radios without a known band are unchanged.

### Changed
- **Licence**: from this release, DCS Mission Tools is licensed under the GNU AGPL-3.0-or-later instead of MIT: any use, commercial included, must publish its source under the same licence, hosted services included; an additional term (section 7(b)) requires every interface to keep the credit line *Based on Mission Tools by MirabelleBenou and the 4th VEAW virtual wing*, now shown at the bottom of the board and of each tool's start screen. Releases up to v1.3.0 remain under MIT. The pydcs tables (LGPL-3.0-or-later) and Goldwolf's drawings keep their own terms.
- **Loadout Editor**: a livery can now be applied to aircraft of any country; the summary warns that the DCS mission editor does not offer it for that country, while the game shows it.

### Fixed
- **Comm Plan Editor** and **Ground Unit Swapper**: on a narrow screen the footer wraps instead of pushing the *Save* button off-screen; the Ground Unit Swapper's unit counter follows the language.
- **Comm Plan Editor**: radio names now follow the DCS World mission editor for the A-10C II, C-130J-30, M-2000C, OH-58D Kiowa Warrior, SA342 Gazelle, F-15E and AV-8B — only the Gazelle's FM radio has presets in the mission (its UHF and VHF AM radios have none), the Kiowa gets a fourth radio and the Harrier a third — and these radios now show their frequency band, except the M-2000C's V/UHF radio.
- **Loadout Editor**: with *Symmetric* ticked in *Compose a loadout*, the twin station now gets the mirror weapon when it has its own left/right reference (F-4E) or another reference with the same name (Mi-24P), and a station says when its twin has no equivalent — the same rule as Mission Plan's Flight Configurator.
- **Loadout Editor**: a weapon offered on both sides under the same name now shows its side (*left* / *right*), e.g. the Mi-24P's Kord door guns; choosing the Kord on one door removes it from the other and says so, as it can only be fitted on one door.
- **All tools**: on a narrow screen (under 560 px) the header now takes two lines — back, tool name and language, then version and file name — instead of running off the right edge; the loaded file name stays readable.
- **Loadout Editor**: the take-off weight in *Compose a loadout* no longer takes the fuel of selected aircraft whose loadout cannot be changed; a setting typed while none of the selected aircraft can take it now stays in the summary, applied to 0 aircraft, instead of vanishing.

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
