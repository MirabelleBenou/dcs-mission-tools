# Tests

Two benches, both run **from the repository root**. Neither touches the repository: the missions the round-trip bench writes
go to a temporary folder.

| Bench | Command | Needs |
|---|---|---|
| Lua table separators | `python3 -B tests/test_lua_separators.py` | Python 3.10 or later, and Node |
| Round trips | `python3 -B tests/run_roundtrips.py [mission.miz ...]` | Python 3.10 or later, `pip install playwright lupa`, a Chromium for Playwright |

`pip install -r tests/requirements.txt` installs the Python packages. Playwright needs a Chromium: either `playwright install chromium`,
or point `PLAYWRIGHT_BROWSERS_PATH` at a folder that already has one.

## Lua table separators — `test_lua_separators.py`

What it proves: the parser block shared by the four tools (`parser_block.py`) follows the grammar of Lua tables — no separator
before the first field, exactly one `,` or `;` between two fields, at most one after the last — both when a mission is opened
and when the text about to be written is checked. Under Node, for each module, on four samples (the DCS mission editor format, the
pydcs format, fields separated by `;`, a mix of `,` and `;`), each also with CRLF line ends: the sample is accepted; the sample
without one separator is refused if the separator stood between two fields and accepted if it was the last of its table; a
doubled separator, or one right after a `{`, is refused. One `[OK]` line per module and sample with its number of cases; the
first wrong case prints a `[FAIL]` line that names it, and the exit code is 1.

## Round trips — `run_roundtrips.py`

What it proves: a mission survives each tool that writes a `.miz`, and what the tools write is a mission that DCS-side Lua reads.
For each mission and for each of the Comm Plan Editor, Ground Unit Swapper, Weather Editor and Loadout Editor (opened from `modules/`
in a headless Chromium):

- **(a)** a round trip with no change, by the tool's own functions: the mission text and every entry of the archive come back identical
  (the Ground Unit Swapper and the Weather Editor have no function that rebuilds the archive: the bench repeats the lines of their *Save* that do,
  with no patch). A mission that the tool refuses — an error message, or no answer within 30 s — is a `[FAIL]` on this case, with the text of the message;
- **(b)** one change made on screen with real clicks, then *Save*: the only data that differ from the original are in the `mission`
  entry, no entry is lost or added, the file name carries a single `_<tool>_<date>-<time>` suffix;
- **(c)** the written file read back by the tool (no error message) and by an independent Lua interpreter ([lupa](https://pypi.org/project/lupa/)):
  every Lua entry runs and is valid UTF-8.

A page error or a `console.error` during (a) or (b) is a `[FAIL]` on that case.

Then, for the Loadout Editor: a country change within the side, a country change to the other side (the moved groups are exactly those
of the checked type, at the chosen side and country, their content changing only by callsign and onboard number, nothing else
changing, the Lua structure sound), and the check that the countries of a side that the file has no `country` table for are greyed out.

One line per case — `[OK]`, `[FAIL]` or `[SKIP]` (nothing to edit or no country to go to, only for a mission given on the command line).
The exit code is 1 after a `[FAIL]`, 0 otherwise, 2 only if the bench cannot run (Playwright, Chromium or lupa missing, mission not found).
A refused mission does not stop the bench (the next tool goes on); any other `[FAIL]` does. The path of the folder that keeps the written
missions is printed whenever the end is not all `[OK]`.

```
python3 -B tests/run_roundtrips.py                      # the three missions of tests/fixtures/
python3 -B tests/run_roundtrips.py my_mission.miz       # a mission of your own (saved by DCS's mission editor), kept private
python3 -B tests/run_roundtrips.py --tools le --out /tmp/rt   # one tool, and keep the written missions in /tmp/rt
```

Options: `--repo DIR` (the repository root; default: the parent of `tests/`), `--out DIR` (where the written missions go; default: a
temporary folder, removed when everything passes), `--tools cp,gu,wx,le`.

### The files

- `fixtures/demo_mission.miz` — a neutral Caucasus mission (Mi-24P, Mi-8MT, F-4E, ground groups, weather); `fixtures/make_demo_miz.py` builds it (pydcs 1.0.0).
- `fixtures/pydcs.miz` — a mission as written by pydcs 1.0.0 and the generators built on it (no trailing comma, no neutral side);
  `fixtures/fixture_pydcs.py` builds it (pydcs 1.0.0).
- `fixtures/accents.miz` — the demo mission with difficult names (accents, Cyrillic, escaped quotes, `$&` and `$'`, a backslash, markup)
  and two joined entries with non-ASCII names; `fixtures/fixture_accents.py <demo_mission.miz> <out.miz>` builds it (standard library only).
- `miz_diff.py` — compares two `.miz`: Lua entries by running them, other entries byte for byte (`python3 -B tests/miz_diff.py before.miz after.miz`).
- `allers_retours.py` — cases (a), (b), (c) for one mission (`python3 -B tests/allers_retours.py . mission.miz label out_dir [cp,gu,wx,le]`).
- `le_pays.py` — the Loadout Editor country cases for one mission (`python3 -B tests/le_pays.py . mission.miz label out_dir`).
- `deplacements.py` — compares a mission before and after a country change (`python3 -B tests/deplacements.py before.miz after.miz`).

The fixtures hold no real unit or person name. `.miz` files are otherwise ignored by git (`.gitignore`): the three above
were added explicitly, and a mission of your own stays out of the repository.
