#!/usr/bin/env python3
"""allers_retours.py <repo> <mission.miz> <label> <out_dir> [tools=cp,gu,wx,le]

Round trips of one mission through each tool that writes a .miz (cp: Comm Plan Editor, gu: Ground Unit Swapper,
wx: Weather Editor, le: Loadout Editor). The trials go through the shell: a tool no longer opens on its own (a module file shows
one line that points to Mission Tools), so each case opens dist/dcs_mission_tools.html in a headless Chromium, enters the tool by
its tile, and does in the tool's iframe what it did in the module alone. Rebuild dist/ (python3 build_mission_tools.py) before
running them: the bench reads the built file, never modules/.
  (a) a round trip WITHOUT any change, by the tool's own functions (text read back, applyPatches with no patch,
      retokenizeSafety, rebuild of the zip as Save does): the mission text and every entry must come back identical;
  (b) one change made on screen with real clicks, then Save, the downloaded file kept: the only data that differ from the
      original are in the `mission` entry (at least one), no entry lost or added, the name carries a single suffix;
  (c) the written file read back by the tool itself (no error toast, no page error) and by an independent Lua
      interpreter (miz_diff.py, lupa): every Lua entry runs and is valid UTF-8.
A mission that the tool refuses (an error message, or no answer within 30 s) is a failure of case (a), not a crash; so is a
page error or a console.error during (a) or (b).
For the Ground Unit Swapper and the Weather Editor, (a) uses a copy of the zip rebuild of their Save (they have no function of that
name): the bench writes the same few lines as their Save does, with no patch.
Writes <out_dir>/<label>_<tool>_{a,b}.miz. Needs: pip install playwright lupa (and a Chromium for Playwright)."""
import os
import re
import sys
import base64
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import miz_diff  # noqa: E402

SHELL = 'dist/dcs_mission_tools.html'   # the built file: the only page the tools run in
MODS = ('cp', 'gu', 'wx', 'le')
NAMES = {'cp': 'Comm Plan Editor', 'gu': 'Ground Unit Swapper', 'wx': 'Weather Editor', 'le': 'Loadout Editor'}
TOKENS = {'cp': 'radios', 'gu': 'swapped', 'wx': 'weather', 'le': 'loadout'}
STAMPED = re.compile(r'_(?:radios|swapped|weather|loadout)_\d{8}-\d{6}')

# (a) the zip as the tool rebuilds it, with no patch at all
JS_A = {
    'cp': "async()=>{const s=UI_STATE.model.source._text;const p=applyPatches(s,[]);retokenizeSafety(p);const b=await rebuildMiz(p,UI_STATE.model);return [p===s, await blobB64(b)]}",
    'gu': "async()=>{const s=UI_STATE.model.source._text;const p=applyPatches(s,[]);retokenizeSafety(p);const z=new JSZip();z.file('mission',p);for(const [n,d] of Object.entries(UI_STATE.model.source._otherFilesData||{}))z.file(n,d);const b=await z.generateAsync({type:'blob',compression:'DEFLATE',compressionOptions:{level:6}});return [p===s, await blobB64(b)]}",
    'wx': "async()=>{const m=UI_STATE.model;const s=m._text;const p=applyPatches(s,[]);retokenizeSafety(p);const z=new JSZip();z.file('mission',p);for(const [n,d] of Object.entries(m._otherFilesData))z.file(n,d);const b=await z.generateAsync({type:'blob',compression:'DEFLATE'});return [p===s, await blobB64(b)]}",
    'le': "async()=>{const s=UI_STATE.model.source._text;const p=applyPatches(s,[]);retokenizeSafety(p);const b=await rebuildMizHQ(p);return [p===s, await blobB64(b)]}",
}
B64 = ("()=>{window.blobB64=async b=>{const u=new Uint8Array(await b.arrayBuffer());let s='';"
       "for(let i=0;i<u.length;i+=0x8000)s+=String.fromCharCode.apply(null,u.subarray(i,i+0x8000));return btoa(s)}}")
TOAST = "()=>{const t=document.getElementById('mtb-toast');return t?t.className+' | '+t.textContent.trim():''}"
SPINNER_DONE = "!(document.getElementById('mtb-spinner')||{classList:{contains:()=>false}}).classList.contains('open')"
FR = "try{for(const k of ['lang_v1','cpe_lang_v1','gus_lang_v1','wx_lang_v1','le_lang_v1'])localStorage.setItem(k,'fr')}catch(e){}"


class NothingToEdit(Exception):
    pass


class LoadRefused(Exception):
    """The tool did not accept the mission: an error message came up, or nothing happened within the time allowed."""


LOAD_WAIT_MS = 30000


def tool_url(repo, mod):
    """The address of a tool: the built shell, with the tool's id after a `#` (the shell ignores it; ToolPage.goto reads it)."""
    p = Path(repo, SHELL).resolve()
    if not p.is_file():
        raise FileNotFoundError(f'{p} not found: build it first (python3 build_mission_tools.py)')
    return p.as_uri() + '#' + mod


# What stays on the page itself when a tool is open; everything else (locator, evaluate, click, set_input_files, wait_for_*...) is
# done in the tool's iframe.
_PAGE_LEVEL = {'keyboard', 'mouse', 'expect_download', 'on', 'add_init_script', 'set_default_timeout', 'context', 'close', 'url'}


class ToolPage:
    """A page of the shell that acts as the page of one tool: `goto(tool_url(...))` opens the shell, enters the tool by its tile, and
    waits for the tool in its iframe; from then on locator, evaluate, click, wait_for_* ... apply to that iframe, and keyboard,
    downloads and events to the page. The cases written for a module opened alone therefore run unchanged in the shell."""

    def __init__(self, page):
        self._page = page
        self._frame = None

    def goto(self, url, **kw):
        base, _, mod = url.partition('#')
        self._frame = None
        self._page.goto(base, wait_until='load')
        if not mod:
            return None
        self._page.locator(f'.module-card[aria-label="{NAMES[mod]}"]').click()
        self._page.wait_for_selector(f'#iframe-{mod}', state='attached')
        frame = self._page.locator(f'#iframe-{mod}').element_handle().content_frame()
        frame.wait_for_function("document.readyState === 'complete' && typeof UI_STATE !== 'undefined'", timeout=60000)
        # the tool is the tool: it keeps its « ◄ Mission Tools » and shows no line that points to Mission Tools
        shown = frame.evaluate("({back: !!document.querySelector('.mt-back-injected'), file: !!document.getElementById('file-input'),"
                               " header: !!document.getElementById('app-header'), line: !!document.querySelector('a[href^=\"https://mirabellebenou.github.io/\"]')})")
        if not (shown['back'] and shown['file'] and shown['header']) or shown['line']:
            raise RuntimeError(f'the shell did not open {NAMES[mod]} as a tool: {shown}')
        self._frame = frame
        return None

    def __getattr__(self, name):
        if self._frame is not None and name not in _PAGE_LEVEL and hasattr(self._frame, name):
            return getattr(self._frame, name)
        return getattr(self._page, name)


def new_page(browser, errors):
    """A page with a 1280 x 900 viewport, French, downloads accepted; page errors and console errors (those of the shell and of the
    tool's iframe) go to `errors`. Returns (context, ToolPage)."""
    ctx = browser.new_context(viewport={'width': 1280, 'height': 900}, accept_downloads=True, locale='fr-FR')
    page = ToolPage(ctx.new_page())
    page.set_default_timeout(120000)
    page.on('pageerror', lambda e: errors.append('pageerror ' + str(e)[:200]))
    page.on('console', lambda m: errors.append('console.error ' + m.text[:200]) if m.type == 'error' else None)
    page.add_init_script(FR)
    return ctx, page


def load_mission(page, miz, wait_ms=LOAD_WAIT_MS):
    """Opens a mission in the tool. Waits for the bottom bar or an error message, `wait_ms` at most; a refusal or a timeout raises
    LoadRefused (with the text of the message, if there is one)."""
    page.set_input_files('#file-input', str(miz))
    waited = 0
    while waited < wait_ms:
        state = page.evaluate("""()=>{const b=document.getElementById('modifications-bar');
            const t=document.getElementById('mtb-toast');
            return {bar: !!b && !b.classList.contains('hidden'),
                    err: t && /(^|\\s)error(\\s|$)/.test(t.className) ? t.textContent.trim() : ''}}""")
        if state['err']:
            raise LoadRefused('the tool refused the mission: ' + state['err'][:200])
        if state['bar']:
            break
        page.wait_for_timeout(200)
        waited += 200
    else:
        toast = page.evaluate(TOAST)
        raise LoadRefused(f'no answer from the tool within {wait_ms // 1000} s' + (f' (message: {toast[:200]})' if toast else ''))
    try:
        page.wait_for_function(SPINNER_DONE, timeout=max(1000, wait_ms - waited))
    except Exception:
        raise LoadRefused(f'the tool was still busy after {wait_ms // 1000} s')


def pick(page, trigger, text):
    """Opens a themed list (button .tbm-trigger) and picks the option whose label contains `text`."""
    trigger.click()
    page.wait_for_timeout(150)
    page.locator('ul[role=listbox] li[role=option]:visible', has_text=text).first.click()
    page.wait_for_timeout(200)


def edit(page, mod):
    """The typical change of each tool, made on screen. Returns a note of what was done."""
    if mod == 'cp':
        inp = page.locator('.freq-input:not([disabled])')
        if inp.count() == 0:
            raise NothingToEdit('no editable radio channel')
        inp = inp.first
        v = float(inp.input_value() or 0)
        nv = f'{v + 0.5:.3f}'
        inp.fill(nv)
        inp.press('Tab')
        return f'first channel {v:.3f} -> {nv}'
    if mod == 'gu':
        if page.locator('.row-chk').count() == 0:
            raise NothingToEdit('no ground unit')
        sk = page.locator('.skill-sel').first
        cur = (sk.text_content() or '').strip()
        target = 'Excellent' if cur != 'Excellent' else 'Average'
        pick(page, sk, target)
        cell = page.locator('.combobox-cell').nth(1) if page.locator('.combobox-cell').count() > 1 else page.locator('.combobox-cell').first
        cell.click()
        page.wait_for_timeout(200)
        page.keyboard.press('ArrowDown')
        page.keyboard.press('ArrowDown')
        page.keyboard.press('Enter')
        page.wait_for_timeout(250)
        return f'skill of the first unit {cur} -> {target}, type of the second unit -> first of the list'
    if mod == 'wx':
        sp = page.locator('#f-wind-ground-speed')
        v = float(sp.input_value() or 0)
        sp.fill(str(int(v) + 3))
        sp.press('Tab')
        d = page.locator('#f-wind-2000-dir')
        d.fill('123')
        d.press('Tab')
        tm = page.locator('#f-time')
        tm.fill('14:45')
        tm.press('Tab')
        return f'ground wind {v} -> {int(v) + 3} m/s, wind at 2000 m direction -> 123, time -> 14:45'
    if mod == 'le':
        chks = page.locator('.type-chk')
        n = chks.count()
        if n == 0:
            raise NothingToEdit('no aircraft')
        chks.nth(n - 1).check()
        page.wait_for_timeout(600)
        cards = page.locator('.ld-card')
        nc = cards.count()
        if nc:
            cards.nth(min(1, nc - 1)).click()
            page.wait_for_timeout(300)
        fuel = page.locator('#set-fuel')
        if fuel.count() and fuel.is_enabled():
            v = float(fuel.input_value() or 0)
            fuel.fill(f'{max(0, v * 0.9):.0f}')
            fuel.press('Tab')
        page.locator('.bar-go').click()
        page.wait_for_timeout(600)
        return f'last type, {nc} loadout(s) in the panel, loadout {"B" if nc > 1 else "A"} and fuel -10 %, Apply to selection'
    raise ValueError(mod)


def problems(rep):
    """What a comparison reports as wrong regardless of the change: entries lost, added, binary entries changed, Lua that does not
    run, bytes that are not UTF-8."""
    bad = {}
    for k in ('lost', 'added', 'bytes_differ', 'unreadable', 'invalid_utf8'):
        if rep[k]:
            bad[k] = rep[k]
    return bad


def check_a(rep, same_text):
    bad = problems(rep)
    if not same_text:
        bad['text'] = 'the mission text changed with no patch'
    for n, v in rep['lua'].items():
        if not v['identical'] or v['changes']:
            bad[n] = f"{len(v['changes'])} change(s), identical bytes: {v['identical']}"
    return bad


def check_b(rep, saved_name, token):
    bad = problems(rep)
    other = {n: len(v['changes']) for n, v in rep['lua'].items() if n != 'mission' and v['changes']}
    if other:
        bad['other_entries_changed'] = other
    if not rep['lua'].get('mission', {}).get('changes'):
        bad['no_change'] = 'the mission entry does not differ from the original'
    stem = saved_name[:-4] if saved_name.lower().endswith('.miz') else saved_name
    if not re.search(r'_' + token + r'_\d{8}-\d{6}$', stem):
        bad['name'] = f'{saved_name}: does not end with _{token}_<stamp>'
    elif len(STAMPED.findall(stem)) != 1:
        bad['name'] = f'{saved_name}: more than one tool suffix'
    return bad


def run_tool(browser, repo, mod, miz, out, label):
    """Runs (a), (b), (c) for one tool. Returns { 'skip': str|None, 'errors': [...], 'a': {...}, 'b': {...}, 'c': {...} };
    each of a, b, c is { 'bad': {...}, 'note': str }."""
    miz = Path(miz)
    res = {'skip': None, 'refused': False, 'errors': [], 'a': None, 'b': None, 'c': None}
    errors = res['errors']
    ctx, page = new_page(browser, errors)
    try:
        page.goto(tool_url(repo, mod), wait_until='load')
        try:
            load_mission(page, miz)
        except LoadRefused as e:
            res['refused'] = True
            res['a'] = {'bad': {'load': str(e)}, 'note': ''}
            return res
        page.evaluate(B64)
        same, b64 = page.evaluate(JS_A[mod])
        pa = os.path.join(out, f'{label}_{mod}_a.miz')
        with open(pa, 'wb') as fh:
            fh.write(base64.b64decode(b64))
        res['a'] = {'bad': check_a(miz_diff.compare(str(miz), pa), same), 'note': 'text and entries identical'}
        if errors:   # a page error or a console.error while the mission was opened and rebuilt
            res['a']['bad']['page_errors'] = errors[0]
        n_a = len(errors)
        try:
            note = edit(page, mod)
        except NothingToEdit as e:
            res['skip'] = str(e)
            return res
        page.wait_for_selector('#btn-save:not([disabled])', timeout=10000)
        with page.expect_download(timeout=180000) as dl:
            page.click('#btn-save')
        d = dl.value
        pb = os.path.join(out, f'{label}_{mod}_b.miz')
        d.save_as(pb)
        page.wait_for_timeout(1500)
        toast_b = page.evaluate(TOAST)
        rep = miz_diff.compare(str(miz), pb)
        nchg = len(rep['lua'].get('mission', {}).get('changes', []))
        res['b'] = {'bad': check_b(rep, d.suggested_filename, TOKENS[mod]),
                    'note': f'{note}; {nchg} change(s) in mission, saved as {d.suggested_filename}'}
        if 'success' not in toast_b.split(' | ')[0]:
            res['b']['bad']['toast'] = 'no success toast after Save: ' + toast_b[:120]
        if len(errors) > n_a:   # a page error or a console.error during the change or the Save
            res['b']['bad']['page_errors'] = errors[n_a]
        # (c) the written file, read by the tool itself in a fresh page
        n_before = len(errors)
        page.goto(tool_url(repo, mod), wait_until='load')
        try:
            load_mission(page, pb)
        except LoadRefused as e:
            res['c'] = {'bad': {'tool_read': str(e)}, 'note': ''}
            return res
        page.wait_for_timeout(800)
        toast_c = page.evaluate(TOAST)
        bad_c = {}
        if toast_c.split(' | ')[0].find('error') >= 0 or not toast_c:
            bad_c['tool_read'] = 'the tool did not accept the written file: ' + toast_c[:120]
        if len(errors) > n_before:
            bad_c['page_errors'] = errors[n_before:][:3]
        for k in ('unreadable', 'invalid_utf8'):
            if rep[k]:
                bad_c['lua_' + k] = rep[k]
        res['c'] = {'bad': bad_c, 'note': 'read back by the tool and by Lua'}
    finally:
        ctx.close()
    return res


def main(argv):
    from playwright.sync_api import sync_playwright
    repo, miz, label, out = argv[1:5]
    mods = argv[5].split(',') if len(argv) > 5 else list(MODS)
    os.makedirs(out, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=['--no-sandbox'])
        for mod in mods:
            r = run_tool(browser, os.path.abspath(repo), mod, miz, out, label)
            print('==', mod, 'skip:' + r['skip'] if r['skip'] else '')
            for k in ('a', 'b', 'c'):
                if r[k]:
                    print('  ', k, 'FAIL ' + str(r[k]['bad']) if r[k]['bad'] else 'ok', '-', r[k]['note'])
            if r['errors']:
                print('   errors:', r['errors'][:5])
        browser.close()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
