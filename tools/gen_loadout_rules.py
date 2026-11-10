#!/usr/bin/env python3
"""Génère data/loadout_rules.json (les règles entre stations que les définitions des appareils de DCS World imposent à
l'éditeur de mission : un emport qui en exclut un autre, ou qui l'exige) depuis le relevé de tools/read_payload_rules.py
et data/aircraft_pylons.json.

Usage :
    pip install lupa
    python3 -I tools/read_payload_rules.py "<DCS World>/CoreMods/aircraft" /tmp/payload_rules.json
    python3 -I tools/gen_loadout_rules.py /tmp/payload_rules.json

Sources :
- le relevé (<relevé.json>), écrit par tools/read_payload_rules.py à partir des définitions Lua des appareils
  (CoreMods/aircraft/<type>/) : par type, une ligne par emport qui porte une règle,
  {"st": <station>, "clsid": …, "required": [{"st", "loadout"}], "forbidden": [{"st", "loadout"}]} ; `loadout` est une
  liste de CLSID, null ou [], et peut contenir "" ou "<CLEAN>" (station vide) ;
- data/aircraft_pylons.json : les CLSID (`clsids`) et, par type et par station, ceux qu'elle accepte (`types`).

Réduction, pour chaque type du relevé présent dans `types` ; al(s) = les CLSID permis à la station s du type. Une ligne
(sa, c) n'est gardée que si c est dans al(sa). Pour chacune de ses règles (sb, L) — sb == sa et une sb absente du type
sont écartées ; « vide » = "" ou "<CLEAN>", N = les CLSID de L non vides et dans al(sb) :
- forbidden : L nul ou [] -> exclusion (sa, sb, toute charge) ; L qui ne contient que du vide -> écartée (sens non
  établi) ; sinon N non vide -> exclusion (sa, sb, N), N vide -> écartée ;
- required : L qui ne contient que du vide -> exclusion (sa, sb, toute charge) ; N non vide et aucun vide dans L ->
  exigence (sa, sb, N) ; sinon écartée (exigence que le Loadout Editor ne connaît pas).
Les règles de clé (sa, sb, N) regroupent les index de c.

Sortie : data/loadout_rules.json
    {"<type>": {"r": [[sa, [ia, …], sb, [ib, …]], …], "x": [[sa, [ia, …], sb, [ib, …] | null], …]}, …}
`sa`, `sb` : numéros de station en chaîne ; `ia`, `ib` : index dans `clsids` de aircraft_pylons.json.
- x (exclusions) : un CLSID de `ia` en `sa` ne va pas avec un CLSID de `ib` en `sb` ; `ib` nul : avec toute charge
  (`sb` doit rester vide) ;
- r (exigences) : un CLSID de `ia` en `sa` exige en `sb` un CLSID de `ib`.
Chaque liste est triée par (int(sa), int(sb), 0 si ib est nul sinon 1, ib, ia). Un type sans règle n'apparaît pas ; un
type qui en a porte toujours `r` et `x`. Écriture : json.dumps compact, clés triées, UTF-8,
fin de ligne \\n. Bibliothèque standard seulement.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PYLONS = os.path.join(HERE, '..', 'data', 'aircraft_pylons.json')
OUT = os.path.join(HERE, '..', 'data', 'loadout_rules.json')
EMPTY = ('', '<CLEAN>')


def reduce_type(rows, index, allowed):
    """(r, x) d'un type : rows = lignes du relevé ; index = CLSID -> index ; allowed = {station: {index permis}}."""
    r_groups, x_groups = {}, {}

    def add(groups, sa, sb, n, ia):
        groups.setdefault((str(sa), str(sb), n), set()).add(ia)

    for row in rows:
        sa, c = row['st'], row['clsid']
        ia = index.get(c)
        if ia is None or ia not in allowed.get(str(sa), ()):
            continue
        for kind in ('forbidden', 'required'):
            for rule in row.get(kind) or []:
                sb, loadout = rule['st'], rule.get('loadout')
                if sb == sa or str(sb) not in allowed:
                    continue
                only_empty = bool(loadout) and all(s in EMPTY for s in loadout)
                n = tuple(sorted({index[s] for s in (loadout or []) if s not in EMPTY and s in index
                                  and index[s] in allowed[str(sb)]}))
                if kind == 'forbidden':
                    if not loadout:
                        add(x_groups, sa, sb, None, ia)
                    elif only_empty:
                        continue
                    elif n:
                        add(x_groups, sa, sb, n, ia)
                else:
                    if only_empty:
                        add(x_groups, sa, sb, None, ia)
                    elif n and not any(s in EMPTY for s in loadout):
                        add(r_groups, sa, sb, n, ia)

    def finish(groups):
        out = [[sa, sorted(ias), sb, None if n is None else list(n)] for (sa, sb, n), ias in groups.items()]
        out.sort(key=lambda e: (int(e[0]), int(e[2]), 0 if e[3] is None else 1, e[3] or [], e[1]))
        return out

    return finish(r_groups), finish(x_groups)


def build(survey, pylons):
    index = {c: i for i, c in enumerate(pylons['clsids'])}
    out = {}
    for typ in sorted(survey):
        if typ not in pylons['types']:
            continue
        allowed = {st: set(lst) for st, lst in pylons['types'][typ].items()}
        r, x = reduce_type(survey[typ], index, allowed)
        if r or x:
            out[typ] = {'r': r, 'x': x}
    return out


def main(argv):
    if len(argv) != 2:
        print(__doc__.split('Usage :')[1].split('Sources :')[0], file=sys.stderr)
        return 2
    with open(argv[1], encoding='utf-8') as fh:
        survey = json.load(fh)
    with open(PYLONS, encoding='utf-8') as fh:
        pylons = json.load(fh)
    table = build(survey, pylons)
    text = json.dumps(table, ensure_ascii=False, separators=(',', ':'), sort_keys=True) + '\n'
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)
    nr = sum(len(v['r']) for v in table.values())
    nx = sum(len(v['x']) for v in table.values())
    print(f'{os.path.relpath(OUT)} : {len(table)} types, {nr} exigences, {nx} exclusions')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
