#!/usr/bin/env python3
"""Génère data/aircraft_pylons.json (type DCS -> pylônes -> emports permis, avec la masse de chaque emport) depuis pydcs.

Usage :
    pip download --no-deps pydcs==1.0.0 -d /tmp/pydcs
    python3 -I tools/gen_aircraft_pylons.py /tmp/pydcs/pydcs-1.0.0-py3-none-any.whl

Source : les modules dcs/planes.py, dcs/helicopters.py et dcs/weapons_data.py de pydcs 1.0.0 (LGPL-3.0-or-later).
L'argument est la roue (.whl) ou un dossier qui contient ces trois fichiers (dcs/planes.py, dcs/helicopters.py,
dcs/weapons_data.py). Les fichiers ne sont pas exécutés : ils sont lus comme du texte Python (ast).

Chaque classe d'appareil qui déclare un `id` et au moins une classe `PylonN` donne une entrée ; chaque attribut de
`PylonN` est un couple (N, Weapons.X) et Weapons.X, dans weapons_data.py, donne le CLSID et la masse (kg).

Sortie : data/aircraft_pylons.json
    {"clsids": [...], "weights": [...], "types": {"<id>": {"<N>": [index, ...]}}}
`clsids` est trié, `weights` est au même rang (kg de pydcs, null s'il manque) ; par type, les pylônes sont dans
l'ordre numérique et, pour chacun, les emports (index dans `clsids`) dans l'ordre de pydcs ; les types sont triés
par clé. UTF-8, fin de ligne \\n. Bibliothèque standard seulement.
"""
import ast
import json
import os
import re
import sys
import warnings
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'data', 'aircraft_pylons.json')
MEMBERS = ('dcs/planes.py', 'dcs/helicopters.py', 'dcs/weapons_data.py')
PYLON_RE = re.compile(r'^Pylon(\d+)$')


def read_sources(path):
    out = []
    if path.lower().endswith('.whl') or zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            for m in MEMBERS:
                out.append(z.read(m).decode('utf-8'))
    else:
        for m in MEMBERS:
            with open(os.path.join(path, m), encoding='utf-8') as fh:
                out.append(fh.read())
    return out


def parse(src):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')   # des "\*" dans des noms de weapons_data.py : sans effet sur leur valeur
        return ast.parse(src)


def weapons_table(src):
    """Attribut de la classe Weapons -> (clsid, masse ou None)."""
    table = {}
    for node in parse(src).body:
        if not (isinstance(node, ast.ClassDef) and node.name == 'Weapons'):
            continue
        for st in node.body:
            if not (isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name)
                    and isinstance(st.value, ast.Dict)):
                continue
            d = {}
            for k, v in zip(st.value.keys, st.value.values):
                if isinstance(k, ast.Constant) and isinstance(v, ast.Constant):
                    d[k.value] = v.value
            clsid, weight = d.get('clsid'), d.get('weight')
            if not isinstance(clsid, str):
                continue
            if isinstance(weight, bool) or not isinstance(weight, (int, float)):
                weight = None
            table[st.targets[0].id] = (clsid, weight)
    return table


def extract(plane_sources, weapons):
    types = {}      # id -> {N -> [clsid, ...]}
    masses = {}     # clsid -> masse ou None
    for src in plane_sources:
        for node in parse(src).body:
            if not isinstance(node, ast.ClassDef):
                continue
            tid = None
            pylons = {}
            for st in node.body:
                if (isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name)
                        and st.targets[0].id == 'id' and isinstance(st.value, ast.Constant)):
                    tid = st.value.value
                if not isinstance(st, ast.ClassDef):
                    continue
                m = PYLON_RE.match(st.name)
                if not m:
                    continue
                lst = []
                for a in st.body:
                    if not (isinstance(a, ast.Assign) and isinstance(a.value, ast.Tuple) and len(a.value.elts) == 2):
                        continue
                    num, ref = a.value.elts
                    if not (isinstance(num, ast.Constant) and isinstance(ref, ast.Attribute)
                            and isinstance(ref.value, ast.Name) and ref.value.id == 'Weapons'):
                        continue
                    if ref.attr not in weapons:
                        sys.exit('Arme inconnue de weapons_data.py : %s (%s, %s)' % (ref.attr, tid, st.name))
                    if num.value != int(m.group(1)):
                        sys.exit('Numéro de pylône incohérent : %s (%s, %s)' % (ref.attr, tid, st.name))
                    clsid, weight = weapons[ref.attr]
                    masses[clsid] = weight
                    if clsid not in lst:
                        lst.append(clsid)
                pylons[int(m.group(1))] = lst
            if not isinstance(tid, str) or not pylons:
                continue
            if tid in types:
                sys.exit('Type en double : %s' % tid)
            types[tid] = pylons
    return types, masses


def render(types, masses):
    clsids = sorted(masses)
    index = {c: i for i, c in enumerate(clsids)}
    j = lambda v: json.dumps(v, ensure_ascii=False, separators=(',', ':'))
    out = ['{"clsids":[']
    out.append(',\n'.join(j(c) for c in clsids))
    out.append('],\n"weights":[')
    out.append(',\n'.join(j(masses[c]) for c in clsids))
    out.append('],\n"types":{')
    rows = []
    for tid in sorted(types):
        body = ','.join('%s:%s' % (j(str(n)), j([index[c] for c in types[tid][n]])) for n in sorted(types[tid]))
        rows.append('%s:{%s}' % (j(tid), body))
    out.append(',\n'.join(rows))
    out.append('}}\n')
    return '\n'.join(out)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    planes, helis, wsrc = read_sources(sys.argv[1])
    weapons = weapons_table(wsrc)
    types, masses = extract((planes, helis), weapons)
    if not types:
        sys.exit('Aucun type trouvé dans ' + sys.argv[1])
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(render(types, masses))
    print('%d types, %d emports -> %s' % (len(types), len(masses), os.path.normpath(OUT)))


if __name__ == '__main__':
    main()
