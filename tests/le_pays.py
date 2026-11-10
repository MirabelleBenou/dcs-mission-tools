#!/usr/bin/env python3
"""le_pays.py <repo> <mission.miz> <label> <out_dir>

Loadout Editor, "Move to country" (the section "Pays de ce type"), with all the aircraft of one type checked (the first type of
the list for the sides check; for a move, the first type that offers a country where to go). Three checks, each returned as a case:
  - sides: a side that the mission file has no `country` table for must show its countries greyed out, each with the reason
    "camp absent du fichier" after a dash; a side that has the table never shows that reason;
  - within the side: the first enabled country of the side of the checked aircraft is chosen, Apply to selection, Save;
  - other side: the first enabled country of another side is chosen, Apply, Save.
A move with no country to go to (for any type) is reported [SKIP].
For each move, the file written is compared with the original: the moved groups are exactly those that left, all of them
at the chosen side and country, their content changing only by `callsign` and `onboard_num`; no other group changes;
nothing changes outside mission.coalition; and the written Lua has a sound structure (deplacements.structure), compared
with the original's.
Needs: pip install playwright lupa."""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deplacements  # noqa: E402
import miz_diff  # noqa: E402
import allers_retours as ar  # noqa: E402

REASON_NO_SIDE = ' — camp absent du fichier'
MENU = ("()=>Array.from(document.querySelectorAll('#country-select optgroup')).map(g=>({label:g.label,"
        "options:Array.from(g.querySelectorAll('option')).map(o=>({value:o.value,text:o.textContent,disabled:o.disabled}))}))")


def sides_with_table(miz):
    """Which of blue, red, neutrals have a `country` table under mission.coalition (read by Lua)."""
    import zipfile
    m = miz_diff.lua_load(zipfile.ZipFile(miz).read('mission').decode('utf-8'), 'mission')
    return {s: isinstance((m.get('coalition', {}).get(s) or {}).get('country'), dict) for s in deplacements.SIDES}


def open_le(browser, repo, miz, errors, check_first=True):
    """Opens the mission in the Loadout Editor; with check_first, ticks the first aircraft type. Returns (context, page), or
    (None, None) when the mission has no aircraft."""
    ctx, page = ar.new_page(browser, errors)
    page.goto(ar.tool_url(repo, 'le'), wait_until='load')
    ar.load_mission(page, miz)
    if page.locator('.type-chk').count() == 0:
        ctx.close()
        return None, None
    if check_first:
        page.locator('.type-chk').nth(0).check()
        page.wait_for_timeout(500)
    return ctx, page


def menu_by_side(page):
    """The country menu as { side: [ {value, text, disabled} ] } in the order shown (the side of the checked aircraft first)."""
    labels = {s: page.evaluate("s=>t('country.camp.'+s)", s) for s in deplacements.SIDES}
    by_label = {v: k for k, v in labels.items()}
    return [(by_label.get(g['label'], g['label']), g['options']) for g in page.evaluate(MENU)]


def check_sides(browser, repo, miz):
    """Returns (status, detail)."""
    errors = []
    ctx, page = open_le(browser, repo, miz, errors)
    if page is None:
        return 'SKIP', 'no aircraft in the mission'
    try:
        has = sides_with_table(miz)
        menu = menu_by_side(page)
        bad = []
        listed = []
        for side, opts in menu:
            listed.append(f'{side}:{len(opts)}')
            for o in opts:
                reason = o['text'].endswith(REASON_NO_SIDE)
                if side in has and not has[side] and not (o['disabled'] and reason):
                    bad.append(f"{side} / {o['text']}: side absent from the file, option not greyed out with its reason")
                if side in has and has[side] and reason:
                    bad.append(f"{side} / {o['text']}: side present in the file, yet marked absent")
        if errors:
            bad.append('page errors: ' + str(errors[:2]))
        absent = [s for s, v in has.items() if not v]
        detail = 'sides without a country table: ' + (', '.join(absent) or 'none') + '; menu groups ' + ' '.join(listed)
        return ('FAIL', '; '.join(bad[:4])) if bad else ('OK', detail)
    finally:
        ctx.close()


def move(browser, repo, miz, out, label, want):
    """want: 'same' (a country of the side of the checked aircraft) or 'other' (a country of another side).
    Returns (status, detail)."""
    errors = []
    ctx, page = open_le(browser, repo, miz, errors, check_first=False)
    if page is None:
        return 'SKIP', 'no aircraft in the mission'
    try:
        # the first aircraft type of the list that offers an enabled country where we want to go
        target = None
        for ti in range(page.locator('.type-chk').count()):
            chk = page.locator('.type-chk').nth(ti)
            chk.check()
            page.wait_for_timeout(500)
            menu = menu_by_side(page)
            groups = menu[:1] if want == 'same' else menu[1:]
            for side, opts in groups:
                for o in opts:
                    if not o['disabled']:
                        target = (side, o)
                        break
                if target:
                    break
            if target:
                break
            chk.uncheck()
            page.wait_for_timeout(300)
        if target is None:
            return 'SKIP', 'no enabled country ' + ('in the side of the checked aircraft' if want == 'same' else 'in another side') + ', for any type'
        side, opt = target
        page.locator('#panel-country .tbm-trigger').click()
        page.wait_for_timeout(200)
        page.locator('ul[role=listbox] li[role=option]:visible', has_text=re.compile('^' + re.escape(opt['text']) + '$')).first.click()
        page.wait_for_timeout(400)
        page.locator('.bar-go').click()
        page.wait_for_timeout(500)
        try:
            with page.expect_download(timeout=60000) as dl:
                page.click('#btn-save')
        except Exception:
            toast = page.evaluate(ar.TOAST)
            return 'FAIL', f'no file written after Save ({opt["text"]}, {side}); toast: {toast[:100]}; Save disabled: ' \
                           f'{page.evaluate("document.getElementById(\'btn-save\').disabled")}'
        out_path = os.path.join(out, f'{label}_le_country_{want}.miz')
        dl.value.save_as(out_path)
        page.wait_for_timeout(800)
        toast = page.evaluate(ar.TOAST)
        res = deplacements.analyse(str(miz), out_path)
        bad = []
        if 'success' not in toast.split(' | ')[0]:
            bad.append('no success toast: ' + toast[:100])
        if not res['moved']:
            bad.append('no group moved')
        want_to = (side, int(opt['value']))
        for gid, l1, l2, keys in res['moved']:
            if (l2[0], l2[1]) != want_to:
                bad.append(f'group {gid} went to {l2[:2]} instead of {want_to}')
            if not set(keys) <= {'callsign', 'onboard_num'}:
                bad.append(f'group {gid}: unexpected keys changed {keys}')
        if res['changed']:
            bad.append(f"groups changed without moving: {[c[0] for c in res['changed']][:5]}")
        if res['lost'] or res['appeared']:
            bad.append(f"groups lost {res['lost'][:5]} / appeared {res['appeared'][:5]}")
        if res['outside']:
            bad.append(f"{len(res['outside'])} change(s) outside mission.coalition, first: {res['outside'][0][0]}")
        before = set(deplacements.structure(str(miz)))
        new = [p for p in deplacements.structure(out_path) if p not in before]
        if new:
            bad.append('structure: ' + '; '.join(new[:3]))
        if errors:
            bad.append('page errors: ' + str(errors[:2]))
        detail = f"{len(res['moved'])} group(s) -> {side} / {opt['text']} ({opt['value']})"
        return ('FAIL', '; '.join(bad[:5])) if bad else ('OK', detail)
    finally:
        ctx.close()


def country_cases(browser, repo, miz, out, label):
    """The three cases of one mission: [(name, status, detail)]."""
    return [
        ('Loadout Editor / sides without a country table are greyed out', *check_sides(browser, repo, miz)),
        ('Loadout Editor / country change within the side', *move(browser, repo, miz, out, label, 'same')),
        ('Loadout Editor / country change to the other side', *move(browser, repo, miz, out, label, 'other')),
    ]


def main(argv):
    from playwright.sync_api import sync_playwright
    repo, miz, label, out = argv[1:5]
    os.makedirs(out, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=['--no-sandbox'])
        for name, status, detail in country_cases(browser, os.path.abspath(repo), Path(miz), out, label):
            print(f'[{status}] {name}: {detail}')
        browser.close()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
