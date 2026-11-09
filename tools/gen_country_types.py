#!/usr/bin/env python3
"""Génère data/country_types.json (pays DCS -> id, nom écrit par l'éditeur, types d'avion et d'hélicoptère permis,
forme et listes d'indicatifs) depuis db_countries.lua de DCS World et pydcs.

Usage :
    pip download --no-deps pydcs==1.0.0 -d /tmp/pydcs
    python3 -I tools/gen_country_types.py <db_countries.lua> /tmp/pydcs/pydcs-1.0.0-py3-none-any.whl

Sources (rien n'est exécuté : le Lua et le Python sont lus comme du texte) :
- db_countries.lua (DCS World, Scripts/Database/) : les pays (`country:add('<CLE>', _("…"), "<nom>", …)`), le nom que
  l'éditeur de missions écrit dans le .miz (3e argument) et, par pays, les types déclarés par
  `cnt_unit(units.Planes.Plane | units.Helicopters.Helicopter, "<type>")` dans son bloc `country:get("<CLE>").Units`
  (lignes et blocs commentés exclus). L'id d'un pays est son rang parmi les `country:add` et les `country:next()`
  (un index sauté : « index 14 is free ») ;
- pydcs 1.0.0 (LGPL-3.0-or-later), dcs/countries.py : les types de la classe `Plane` et de la classe `Helicopter` de
  chaque pays (résolus en `id` par dcs/planes.py et dcs/helicopters.py), `use_western_callsigns` et les listes
  `AWACS`, `Tankers`, `Air` de son `callsign` ; dcs/planes.py et dcs/helicopters.py : la catégorie d'indicatif de chaque
  type (`category` ; `Interceptor` compte pour `Air`, absente : `Air`).

Règle : un type est permis dans un pays si db_countries.lua OU pydcs l'y met ; AGGRESSORS, CJTF_BLUE, CJTF_RED et
UN_PEACEKEEPERS prennent tous les types connus (le jeu les fusionne) ; un type que ni l'une ni l'autre ne connaît n'est
pas contrôlé (il n'est pas dans `types`).

Sortie : data/country_types.json
    {"types": [<type>, …],                       types connus, triés
     "cat": {"<type>": "AWACS" | "Tankers"},     catégorie d'indicatif des types qui ne sont pas « Air »
     "countries": {"<id>": {"name": …, "cs": "name" | "number", "lists": {"AWACS": […], "Tankers": […], "Air": […]},
                            "types": [<index dans types>, …]}, …}}
`lists` n'est écrit que pour un pays dont l'indicatif est un nom. Un pays par ligne, triés par id ; UTF-8, fin de
ligne \\n. Bibliothèque standard seulement.
"""
import ast
import json
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'data', 'country_types.json')
SPECIAL = ('AGGRESSORS', 'CJTF_BLUE', 'CJTF_RED', 'UN_PEACEKEEPERS')
LISTS = ('AWACS', 'Tankers', 'Air')

ADD_RE = re.compile(r"^\s*country:(?:next\(\)|add\(\s*'([^']+)'\s*,\s*_\(\"[^\"]*\"\)\s*,\s*\"([^\"]+)\")", re.M)
BLOCK_RE = re.compile(r'country:get\("([^"]+)"\)\.Units')
UNIT_RE = re.compile(r'cnt_unit\(\s*units\.(?:Planes\.Plane|Helicopters\.Helicopter)\s*,\s*"([^"]+)"')


def read_db(path):
    """(pays, types) : pays = {id: (clé, nom)} ; types = {clé: {type, …}} d'après les blocs Units."""
    with open(path, encoding='utf-8', errors='replace') as fh:
        text = fh.read()
    text = re.sub(r'--\[\[.*?\]\]', '', text, flags=re.S)
    countries, rank = {}, 0
    for m in ADD_RE.finditer(text):
        if m.group(1):
            countries[rank] = (m.group(1), m.group(2))
        rank += 1
    blocks, cur = {}, None
    for line in text.split('\n'):
        if line.lstrip().startswith('--'):
            continue
        m = BLOCK_RE.search(line)
        if m:
            cur = m.group(1)
            blocks.setdefault(cur, set())
            continue
        m = UNIT_RE.search(line)
        if m and cur:
            blocks[cur].add(m.group(1))
    return countries, blocks


def class_attrs(cls):
    """Les affectations de constantes d'une classe : {nom: valeur}."""
    out = {}
    for node in cls.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) \
                and isinstance(node.value, ast.Constant):
            out[node.targets[0].id] = node.value.value
    return out


def read_pydcs(whl):
    """(pays, catégories) : pays = {id: {types, western, lists}} ; catégories = {type: 'Air' | 'AWACS' | 'Tankers'}."""
    with zipfile.ZipFile(whl) as z:
        src = {m: z.read(m).decode('utf-8') for m in ('dcs/planes.py', 'dcs/helicopters.py', 'dcs/countries.py')}
    ids, cat = {}, {}
    for member, mod in (('dcs/planes.py', 'planes'), ('dcs/helicopters.py', 'helicopters')):
        for node in ast.parse(src[member]).body:
            if not isinstance(node, ast.ClassDef):
                continue
            attrs = class_attrs(node)
            if 'id' in attrs:
                ids[(mod, node.name)] = attrs['id']
                kind = attrs.get('category', 'Air')
                cat[attrs['id']] = 'Air' if kind == 'Interceptor' else kind
    countries = {}
    for node in ast.parse(src['dcs/countries.py']).body:
        if not isinstance(node, ast.ClassDef):
            continue
        entry = {'types': set(), 'western': True, 'lists': {}}
        cid = None
        for item in node.body:
            if isinstance(item, ast.Assign) and len(item.targets) == 1 and isinstance(item.targets[0], ast.Name):
                name = item.targets[0].id
                if name == 'id' and isinstance(item.value, ast.Constant):
                    cid = item.value.value
                elif name == 'use_western_callsigns' and isinstance(item.value, ast.Constant):
                    entry['western'] = bool(item.value.value)
                elif name == 'callsign' and isinstance(item.value, ast.Dict):
                    for key, val in zip(item.value.keys, item.value.values):
                        if key.value in LISTS:
                            entry['lists'][key.value] = [e.attr for e in val.elts]
            elif isinstance(item, ast.ClassDef) and item.name in ('Plane', 'Helicopter'):
                for sub in item.body:
                    if isinstance(sub, ast.Assign) and isinstance(sub.value, ast.Attribute) \
                            and isinstance(sub.value.value, ast.Name):
                        key = (sub.value.value.id, sub.value.attr)
                        if key not in ids:
                            sys.exit('Type introuvable dans pydcs : %s.%s (%s)' % (key[0], key[1], node.name))
                        entry['types'].add(ids[key])
        if cid is not None:
            countries[cid] = entry
    return countries, cat


def build(db_path, whl):
    db_countries, db_types = read_db(db_path)
    py_countries, cat = read_pydcs(whl)
    known = set()
    for entry in py_countries.values():
        known |= entry['types']
    for types in db_types.values():
        known |= types
    types = sorted(known)
    index = {t: i for i, t in enumerate(types)}
    countries = {}
    for cid in sorted(db_countries):
        key, name = db_countries[cid]
        if cid not in py_countries:
            sys.exit('Pays %d (%s) absent de pydcs' % (cid, key))
        py = py_countries[cid]
        allowed = known if key in SPECIAL else (py['types'] | db_types.get(key, set()))
        row = {'name': name, 'cs': 'name' if py['western'] else 'number'}
        if py['western']:
            row['lists'] = {k: py['lists'][k] for k in LISTS if k in py['lists']}
        row['types'] = sorted(index[t] for t in allowed)
        countries[str(cid)] = row
    return {'types': types, 'cat': {t: cat[t] for t in types if t in cat and cat[t] != 'Air'},
            'countries': countries}


def render(doc):
    j = lambda v: json.dumps(v, ensure_ascii=False, separators=(',', ':'))
    out = ['{"types":[']
    out.append(',\n'.join(j(t) for t in doc['types']))
    out.append('],\n"cat":' + j(doc['cat']) + ',\n"countries":{')
    out.append(',\n'.join('%s:%s' % (j(k), j(v)) for k, v in doc['countries'].items()))
    out.append('}}\n')
    return '\n'.join(out)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    doc = build(sys.argv[1], sys.argv[2])
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(render(doc))
    print('%d pays, %d types connus -> %s' % (len(doc['countries']), len(doc['types']), os.path.normpath(OUT)))


if __name__ == '__main__':
    main()
