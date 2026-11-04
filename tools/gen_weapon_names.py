#!/usr/bin/env python3
"""Génère data/weapon_names.json (CLSID -> nom de l'arme) depuis pydcs.

Usage :
    pip download --no-deps pydcs==1.0.0 -d /tmp/pydcs
    python3 -I tools/gen_weapon_names.py /tmp/pydcs/pydcs-1.0.0-py3-none-any.whl

Source : le module dcs/weapons_data.py de pydcs 1.0.0 (LGPL-3.0-or-later). L'argument est
la roue (.whl) ou le fichier weapons_data.py lui-même. Le fichier n'est pas exécuté : il
est lu comme du texte Python (ast), et chaque entrée de la classe Weapons, un dictionnaire
{"clsid": ..., "name": ..., "weight": ...}, donne une paire CLSID -> nom.

Sortie : data/weapon_names.json, trié par clé, une entrée par ligne, UTF-8, fin de ligne \n.
Bibliothèque standard seulement.
"""
import ast
import json
import os
import sys
import warnings
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'data', 'weapon_names.json')
MEMBER = 'dcs/weapons_data.py'


def read_source(path):
    if path.lower().endswith('.whl') or zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            return z.read(MEMBER).decode('utf-8')
    with open(path, encoding='utf-8') as fh:
        return fh.read()


def extract(src):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')   # le module contient des "\*" dans des noms : sans effet sur leur valeur
        tree = ast.parse(src)
    names = {}
    for node in tree.body:
        if not (isinstance(node, ast.ClassDef) and node.name == 'Weapons'):
            continue
        for st in node.body:
            if not (isinstance(st, ast.Assign) and isinstance(st.value, ast.Dict)):
                continue
            d = {}
            for k, v in zip(st.value.keys, st.value.values):
                if isinstance(k, ast.Constant) and isinstance(v, ast.Constant):
                    d[k.value] = v.value
            clsid, name = d.get('clsid'), d.get('name')
            if not isinstance(clsid, str) or not isinstance(name, str):
                continue
            if clsid in names and names[clsid] != name:
                sys.exit('CLSID en double avec deux noms : %s' % clsid)
            names[clsid] = name
    return names


def render(names):
    return json.dumps(names, ensure_ascii=False, indent=1, sort_keys=True) + '\n'


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    names = extract(read_source(sys.argv[1]))
    if not names:
        sys.exit('Aucune arme trouvée dans ' + sys.argv[1])
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(render(names))
    print('%d armes -> %s' % (len(names), os.path.normpath(OUT)))


if __name__ == '__main__':
    main()
