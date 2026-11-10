#!/usr/bin/env python3
"""Round-trip bench of Mission Tools. Run from the repository root:

    python3 -B tests/run_roundtrips.py [mission.miz ...] [--repo DIR] [--out DIR] [--tools cp,gu,wx,le]

With no mission, it runs the three missions of tests/fixtures/ (demo_mission.miz, pydcs.miz, accents.miz); with arguments,
the missions given (a private mission saved by DCS's mission editor is passed that way). For each mission and each of the four
tools (Comm Plan Editor, Ground Unit Swapper, Weather Editor, Loadout Editor), opened from modules/ in a headless Chromium:
  (a) a round trip with no change;
  (b) one change made on screen, then Save;
  (c) the written file read back by the tool and by a real Lua interpreter (lupa);
then, for the Loadout Editor, a country change within the side, a country change to the other side, and the check that the
countries of a side absent from the file are greyed out.
One line per case, [OK], [FAIL] or [SKIP] (nothing to edit or no country to go to, in a mission given on the command line; a
fixture never skips an edit). Exit code 1 at the first [FAIL], 0 when every case is [OK] or [SKIP], 2 if the bench cannot run.
The missions written by the bench go to a temporary folder outside the repository (kept when a case fails, with its path
printed); --out chooses another folder, which is kept.

Needs: pip install playwright lupa (see tests/requirements.txt), and a Chromium for Playwright."""
import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

FIXTURES = ['demo_mission.miz', 'pydcs.miz', 'accents.miz']


def main():
    ap = argparse.ArgumentParser(description='Round-trip bench of Mission Tools.')
    ap.add_argument('missions', nargs='*', help='missions to run (default: the three of tests/fixtures/)')
    ap.add_argument('--repo', default=str(HERE.parent), help='the repository root (default: the parent of tests/)')
    ap.add_argument('--out', default=None, help='folder for the written missions (default: a temporary folder)')
    ap.add_argument('--tools', default='cp,gu,wx,le', help='tools to run, among cp, gu, wx, le')
    args = ap.parse_args()
    try:
        import lupa  # noqa: F401
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        print(f'[ERROR] {e}: pip install playwright lupa (see tests/requirements.txt)')
        return 2
    import allers_retours as ar
    import le_pays

    repo = os.path.abspath(args.repo)
    fixtures_run = not args.missions
    missions = [Path(m).resolve() for m in args.missions] if args.missions else [HERE / 'fixtures' / f for f in FIXTURES]
    for m in missions:
        if not m.is_file():
            print(f'[ERROR] mission not found: {m}')
            return 2
    tools = [t for t in args.tools.split(',') if t]
    out = args.out or tempfile.mkdtemp(prefix='mt_roundtrips_')
    os.makedirs(out, exist_ok=True)
    failed = False
    counts = {'OK': 0, 'FAIL': 0, 'SKIP': 0}

    def report(status, name, detail):
        nonlocal failed
        counts[status] += 1
        print(f'[{status}] {name}' + (f' : {detail}' if detail else ''), flush=True)
        if status == 'FAIL':
            failed = True

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=['--no-sandbox'])
            for miz in missions:
                label = miz.stem
                for mod in tools:
                    r = ar.run_tool(browser, repo, mod, miz, out, label)
                    who = f'{label} / {ar.NAMES[mod]}'
                    if r['skip']:
                        report('FAIL' if fixtures_run else 'SKIP', f'{who} / nothing to edit', r['skip'])
                        if failed:
                            break
                        continue
                    for key, title in (('a', '(a) round trip with no change'), ('b', '(b) one change on screen, Save'),
                                       ('c', '(c) written file read back by the tool and by Lua')):
                        case = r[key]
                        if case is None:
                            report('FAIL', f'{who} / {title}', 'not reached: ' + '; '.join(r['errors'][:2]))
                        else:
                            report('FAIL' if case['bad'] else 'OK', f'{who} / {title}', str(case['bad']) if case['bad'] else case['note'])
                        if failed:
                            break
                    if failed:
                        break
                if failed:
                    break
                if 'le' in tools:
                    for name, status, detail in le_pays.country_cases(browser, repo, miz, out, label):
                        report(status, f'{label} / {name}', detail)
                        if failed:
                            break
                if failed:
                    break
            browser.close()
    except Exception as e:   # the bench itself could not run (no Chromium, page never loaded...)
        print(f'[ERROR] the bench could not run: {type(e).__name__}: {str(e)[:300]}')
        return 2
    print(f"-- {counts['OK']} OK, {counts['FAIL']} FAIL, {counts['SKIP']} SKIP --")
    if failed:
        print(f'written missions kept in {out}')
        return 1
    if args.out is None:
        shutil.rmtree(out, ignore_errors=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
