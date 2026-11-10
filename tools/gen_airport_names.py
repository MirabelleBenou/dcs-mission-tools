#!/usr/bin/env python3
"""Génère data/airport_names.json (théâtre DCS -> numéro d'aérodrome -> nom) depuis pydcs.

Usage :
    pip download --no-deps pydcs==1.0.0 -d /tmp/pydcs
    python3 -I tools/gen_airport_names.py /tmp/pydcs/pydcs-1.0.0-py3-none-any.whl

Source : les fichiers dcs/terrain/<dossier>/<dossier>.py et dcs/terrain/<dossier>/airports.py de pydcs 1.0.0
(LGPL-3.0-or-later). L'argument est la roue (.whl) ou un dossier qui contient ces fichiers (dcs/terrain/...). Rien
n'est exécuté : les fichiers sont lus comme du texte Python (ast).

- le théâtre est le premier argument de `super().__init__("…"` de la classe du terrain, dans
  dcs/terrain/<dossier>/<dossier>.py : c'est aussi la valeur de `mission.theatre` d'un .miz ;
- les aérodromes sont les classes de dcs/terrain/<dossier>/airports.py qui déclarent `id` et `name`.

Sortie : data/airport_names.json
    {"<théâtre>": {"<id>": "<nom>", …}, …}
Écrit par json.dumps(…, ensure_ascii=False, separators=(',', ':'), sort_keys=True) puis une fin de ligne \\n.
Bibliothèque standard seulement.
"""
import ast
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'data', 'airport_names.json')
PREFIX = 'dcs/terrain/'


def read_members(path):
    """{membre: texte} des fichiers dcs/terrain/<dossier>/<dossier>.py et .../airports.py."""
    out = {}
    if path.lower().endswith('.whl') or (os.path.isfile(path) and zipfile.is_zipfile(path)):
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            for n in names:
                parts = n.split('/')
                if n.startswith(PREFIX) and len(parts) == 4 and parts[3] in (parts[2] + '.py', 'airports.py'):
                    out[n] = z.read(n).decode('utf-8')
    else:
        base = os.path.join(path, 'dcs', 'terrain')
        for d in sorted(os.listdir(base)):
            for f in (d + '.py', 'airports.py'):
                p = os.path.join(base, d, f)
                if os.path.isfile(p):
                    with open(p, encoding='utf-8') as fh:
                        out[PREFIX + d + '/' + f] = fh.read()
    return out


def theatre_name(src, where):
    """Le premier argument de `super().__init__("…"` dans la classe du terrain."""
    for node in ast.parse(src).body:
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if not (isinstance(item, ast.FunctionDef) and item.name == '__init__'):
                continue
            for call in ast.walk(item):
                if (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == '__init__'
                        and isinstance(call.func.value, ast.Call) and isinstance(call.func.value.func, ast.Name)
                        and call.func.value.func.id == 'super'
                        and call.args and isinstance(call.args[0], ast.Constant) and isinstance(call.args[0].value, str)):
                    return call.args[0].value
    sys.exit('Théâtre introuvable dans ' + where)


def airports(src):
    """{id: nom} des classes qui déclarent `id` (entier) et `name` (texte)."""
    out = {}
    for node in ast.parse(src).body:
        if not isinstance(node, ast.ClassDef):
            continue
        attrs = {}
        for st in node.body:
            if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name) \
                    and isinstance(st.value, ast.Constant):
                attrs[st.targets[0].id] = st.value.value
        if isinstance(attrs.get('id'), int) and not isinstance(attrs.get('id'), bool) and isinstance(attrs.get('name'), str):
            if attrs['id'] in out:
                sys.exit('Numéro d\'aérodrome en double : %s (%s)' % (attrs['id'], node.name))
            out[attrs['id']] = attrs['name']
    return out


def build(path):
    members = read_members(path)
    doc = {}
    for n in sorted(members):
        parts = n.split('/')
        if parts[3] != parts[2] + '.py':
            continue
        apt = PREFIX + parts[2] + '/airports.py'
        if apt not in members:
            sys.exit('Aérodromes introuvables : ' + apt)
        theatre = theatre_name(members[n], n)
        if theatre in doc:
            sys.exit('Théâtre en double : ' + theatre)
        doc[theatre] = {str(i): nm for i, nm in airports(members[apt]).items()}
    return doc


def render(doc):
    return json.dumps(doc, ensure_ascii=False, separators=(',', ':'), sort_keys=True) + '\n'


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    doc = build(sys.argv[1])
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(render(doc))
    print('%d théâtres, %d aérodromes -> %s' % (len(doc), sum(len(v) for v in doc.values()), os.path.normpath(OUT)))


if __name__ == '__main__':
    main()
