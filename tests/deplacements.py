#!/usr/bin/env python3
"""deplacements.py <before.miz> <after.miz>

Checks a country or side change made by the Loadout Editor. Pairs the groups by groupId and reports: the groups that moved
(side, country id, category before -> after) with, for each, the keys of its content that change (expected: the callsign
and, at most, onboard_num); the groups that changed without moving; what changes outside mission.coalition (expected:
nothing); and the country tables left without any group. Also exposes structure(path), which checks the written Lua:
every country entry has an id and a name, its id is listed in mission.coalitions under the same side, group ids and unit
ids are unique, group indices have no hole, and no country entry is left empty.

Needs: pip install lupa
"""
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lupa  # noqa: E402
import miz_diff  # noqa: E402

SIDES = ('blue', 'red', 'neutrals')
CATEGORIES = ('plane', 'helicopter', 'vehicle', 'ship', 'static')


def load(path):
    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(zipfile.ZipFile(path).read('mission').decode('utf-8'))
    return miz_diff.to_py(lua.globals().mission)


def groups(m):
    """groupId -> ((side, country id, category), group table)."""
    g = {}
    for side in SIDES:
        for _, ct in ((m['coalition'].get(side) or {}).get('country') or {}).items():
            for cat in CATEGORIES:
                for _, x in ((ct.get(cat) or {}).get('group') or {}).items():
                    g[x.get('groupId')] = ((side, ct.get('id'), cat), x)
    return g


def content_key(path):
    """The key of a group's content that a change path belongs to: `callsign` for anything under a callsign, else the last key."""
    return 'callsign' if '.callsign' in path else path.split('.')[-1].split('[')[0]


def analyse(path_before, path_after):
    """Returns { 'moved': [(groupId, from, to, keys)], 'changed': [(groupId, keys, n)], 'lost': [...], 'appeared': [...],
    'outside': [(path, before, after)], 'empty_tables': [str] }."""
    ma, mb = load(path_before), load(path_after)
    ga, gb = groups(ma), groups(mb)
    res = {'moved': [], 'changed': [], 'lost': [], 'appeared': [], 'outside': [], 'empty_tables': []}
    for gid, (loc, x) in ga.items():
        if gid not in gb:
            res['lost'].append(gid)
            continue
        loc2, y = gb[gid]
        out = []
        miz_diff.diff(x, y, 'g', out)
        keys = sorted({content_key(p) for p, _, _ in out})
        if loc != loc2:
            res['moved'].append((gid, loc, loc2, keys))
        elif out:
            res['changed'].append((gid, keys, len(out)))
    res['appeared'] = sorted(gb.keys() - ga.keys())
    ra = {k: v for k, v in ma.items() if k != 'coalition'}
    rb = {k: v for k, v in mb.items() if k != 'coalition'}
    miz_diff.diff(ra, rb, 'mission', res['outside'])
    for side in SIDES:
        for i, ct in ((mb['coalition'].get(side) or {}).get('country') or {}).items():
            for cat in CATEGORIES:
                if cat in ct and not ((ct[cat] or {}).get('group')):
                    res['empty_tables'].append(f'{side}.country[{i}].{cat}')
    return res


def structure(path):
    """Problems found in the written mission (empty list: none)."""
    try:
        m = load(path)
    except Exception as e:
        return ['UNREADABLE LUA: ' + str(e)[:160]]
    pb = []
    gids, uids = [], []
    side_of = {}
    for side, ids in (m.get('coalitions') or {}).items():
        for _, cid in ids.items():
            side_of[cid] = side
    for side in SIDES:
        co = (m['coalition'].get(side) or {}).get('country') or {}
        for i, ct in co.items():
            if 'id' not in ct or 'name' not in ct:
                pb.append(f'{side}.country[{i}] has no id or name')
            if side_of.get(ct.get('id')) not in (None, side):
                pb.append(f"country {ct.get('id')} under {side} but listed in coalitions.{side_of.get(ct.get('id'))}")
            if side_of.get(ct.get('id')) is None:
                pb.append(f"country {ct.get('id')} under {side} is not listed in mission.coalitions")
            n = 0
            for cat in CATEGORIES:
                gs = ((ct.get(cat) or {}).get('group') or {})
                if gs and sorted(gs.keys()) != list(range(1, len(gs) + 1)):
                    pb.append(f'{side}.country[{i}].{cat}.group: indices {sorted(gs.keys())} (hole)')
                for _, g in gs.items():
                    n += 1
                    gids.append(g.get('groupId'))
                    for _, u in (g.get('units') or {}).items():
                        uids.append(u.get('unitId'))
            if n == 0:
                pb.append(f'{side}.country[{i}] ({ct.get("name")}) has no group')
    if len(gids) != len(set(gids)):
        pb.append('duplicate groupId')
    if len(uids) != len(set(uids)):
        pb.append('duplicate unitId')
    return pb


def main(a, b):
    try:
        res = analyse(a, b)
    except Exception as e:
        print('unreadable mission:', str(e)[:200])
        return 1
    print('moved:', len(res['moved']))
    for gid, l1, l2, k in res['moved']:
        print('  ', gid, l1, '->', l2, 'keys changed:', k)
    print('changed without moving:', len(res['changed']))
    for c in res['changed'][:20]:
        print('  ', c)
    print('outside mission.coalition:', len(res['outside']))
    for p, x, y in res['outside'][:30]:
        print('  ', p, ':', x[:80], '->', y[:80])
    for s in res['empty_tables']:
        print('  ', s, 'left without any group')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
