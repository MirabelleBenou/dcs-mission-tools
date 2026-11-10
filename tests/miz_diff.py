#!/usr/bin/env python3
"""miz_diff.py <before.miz> <after.miz> [--json out.json]

Compares two .miz files as data. The Lua entries (mission, options, warehouses, l10n/*/dictionary, l10n/*/mapResource)
are executed by a real Lua interpreter (lupa) and compared key by key; every other entry (scripts, sounds, images,
kneeboards) is compared byte for byte. Prints the paths that change, in a readable form such as
`mission.coalition.red.country[1].helicopter.group[2].units[1].payload.pylons[3].CLSID : "A" -> "B"`.
Also serves as an independent reader: an entry that does not execute is reported as unreadable.

Needs: pip install lupa
"""
import io
import json
import sys
import zipfile

import lupa

LUA_ENTRIES = ('mission', 'options', 'warehouses')


def is_lua(name):
    return name in LUA_ENTRIES or name.endswith('/dictionary') or name.endswith('/mapResource')


def lua_load(text, name):
    """Runs a Lua entry and returns its main table as nested Python dicts."""
    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(text)
    var = {'mission': 'mission', 'options': 'options', 'warehouses': 'warehouses'}.get(name)
    if var is None:
        var = 'dictionary' if name.endswith('dictionary') else 'mapResource'
    return to_py(lua.globals()[var])


def to_py(v):
    if lupa.lua_type(v) == 'table':
        return {(k if isinstance(k, (int, float)) else str(k)): to_py(x) for k, x in v.items()}
    if isinstance(v, bytes):
        return v.decode('utf-8', 'replace')
    return v


def fmt_key(k):
    return f'[{k}]' if isinstance(k, (int, float)) else f'.{k}'


def short(v):
    s = json.dumps(v, ensure_ascii=False, default=str)
    return s if len(s) <= 160 else s[:157] + '...'


def diff(a, b, path, out, limit=400):
    """Appends (path, before, after) to `out` for every leaf that differs (at most `limit` entries)."""
    if len(out) >= limit:
        return
    if isinstance(a, dict) and isinstance(b, dict):
        for k in a.keys() | b.keys():
            p = path + fmt_key(k)
            if k not in b:
                out.append((p, short(a[k]), '(absent)'))
            elif k not in a:
                out.append((p, '(absent)', short(b[k])))
            else:
                diff(a[k], b[k], p, out, limit)
    elif a != b and not (isinstance(a, float) and isinstance(b, float) and abs(a - b) <= 1e-9 * max(1, abs(a))):
        out.append((path, short(a), short(b)))


def compare(path_a, path_b):
    """Compares two .miz files. Returns a dict:
    lost / added / bytes_differ : entry names (non-Lua entries are compared byte for byte);
    unreadable : Lua entries that do not execute ; invalid_utf8 : Lua entries of the second file that are not UTF-8 ;
    lua : { entry: { 'identical': bool (same bytes), 'changes': [(path, before, after), ...] } }."""
    za, zb = zipfile.ZipFile(path_a), zipfile.ZipFile(path_b)
    na = {i.filename for i in za.infolist() if not i.is_dir()}
    nb = {i.filename for i in zb.infolist() if not i.is_dir()}
    rep = {'lost': sorted(na - nb), 'added': sorted(nb - na), 'bytes_differ': [],
           'lua': {}, 'unreadable': [], 'invalid_utf8': []}
    for n in sorted(na & nb):
        ba, bb = za.read(n), zb.read(n)
        if is_lua(n):
            try:
                bb.decode('utf-8')
            except UnicodeDecodeError:
                rep['invalid_utf8'].append(n)
            short_name = n.split('/')[-1] if '/' in n else n
            try:
                da = lua_load(ba.decode('utf-8', 'surrogateescape'), short_name)
            except Exception as e:
                rep['unreadable'].append(f'{n} (before): {str(e)[:120]}')
                continue
            try:
                db = lua_load(bb.decode('utf-8', 'surrogateescape'), short_name)
            except Exception as e:
                rep['unreadable'].append(f'{n} (after): {str(e)[:120]}')
                continue
            out = []
            diff(da, db, n, out)
            rep['lua'][n] = {'identical': ba == bb, 'changes': out}
        elif ba != bb:
            rep['bytes_differ'].append(n)
    return rep


def main(argv):
    r = compare(argv[1], argv[2])
    if '--json' in argv:
        with open(argv[argv.index('--json') + 1], 'w', encoding='utf-8') as fh:
            json.dump(r, fh, ensure_ascii=False, indent=1)
    for k in ('lost', 'added', 'bytes_differ', 'unreadable', 'invalid_utf8'):
        if r[k]:
            print(k, r[k])
    for n, d in r['lua'].items():
        tag = 'identical bytes' if d['identical'] else f"{len(d['changes'])} change(s)"
        print(f'{n}: {tag}')
        for p, a, b in d['changes'][:60]:
            print(f'   {p} : {a} -> {b}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
