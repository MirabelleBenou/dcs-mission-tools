#!/usr/bin/env python3
"""Génère data/aircraft_limits.json (type DCS -> carburant max et capacités de leurres / paillettes) depuis pydcs.

Usage :
    pip download --no-deps pydcs==1.0.0 -d /tmp/pydcs
    python3 -I tools/gen_aircraft_limits.py /tmp/pydcs/pydcs-1.0.0-py3-none-any.whl

Source : les modules dcs/planes.py et dcs/helicopters.py de pydcs 1.0.0 (LGPL-3.0-or-later). L'argument est
la roue (.whl) ou un dossier qui contient ces deux fichiers (dcs/planes.py, dcs/helicopters.py). Les fichiers ne
sont pas exécutés : ils sont lus comme du texte Python (ast). Chaque classe qui déclare un `id` donne une
entrée ; ses champs fuel_max, flare, chaff, charge_total, flare_charge_size et chaff_charge_size sont recopiés
tels que la classe les déclare, et valent null quand elle ne les déclare pas (le module n'en tire alors aucun
maximum).

Sortie : data/aircraft_limits.json, trié par clé, une entrée par ligne, UTF-8, fin de ligne \n.
Bibliothèque standard seulement.
"""
import ast
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'data', 'aircraft_limits.json')
MEMBERS = ('dcs/planes.py', 'dcs/helicopters.py')
FIELDS = ('fuel_max', 'flare', 'chaff', 'charge_total', 'flare_charge_size', 'chaff_charge_size')


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


def extract(sources):
    limits = {}
    for src in sources:
        for node in ast.parse(src).body:
            if not isinstance(node, ast.ClassDef):
                continue
            d = {}
            for st in node.body:
                if (isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name)
                        and isinstance(st.value, ast.Constant)):
                    d[st.targets[0].id] = st.value.value
            tid = d.get('id')
            if not isinstance(tid, str):
                continue
            if tid in limits:
                sys.exit('Type en double : %s' % tid)
            entry = {}
            for f in FIELDS:
                v = d.get(f)
                entry[f] = v if isinstance(v, (int, float)) and not isinstance(v, bool) else None
            limits[tid] = entry
    return limits


def render(limits):
    lines = []
    for k in sorted(limits):
        lines.append(' %s: %s' % (json.dumps(k, ensure_ascii=False), json.dumps(limits[k], ensure_ascii=False, separators=(',', ':'))))
    return '{\n' + ',\n'.join(lines) + '\n}\n'


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    limits = extract(read_sources(sys.argv[1]))
    if not limits:
        sys.exit('Aucun type trouvé dans ' + sys.argv[1])
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(render(limits))
    print('%d types -> %s' % (len(limits), os.path.normpath(OUT)))


if __name__ == '__main__':
    main()
