#!/usr/bin/env python3
"""Génère data/aircraft_views.json (type DCS -> vue de face + points d'attache des stations) depuis data/views/.

Usage :
    python3 -I tools/gen_aircraft_views.py

Entrée : data/views/stations.json, où chaque type donne le chemin de son dessin (`svg`, relatif à data/, par exemple views/mi24p.svg),
son `viewBox`, le point d'attache de chaque station (unités du viewBox) et les stations hors vue ; data/views/*.svg.
Sortie : data/aircraft_views.json = stations.json où chaque `svg` est remplacé par le texte du fichier
correspondant, tel quel. Même mise en forme que stations.json (un espace d'indentation), UTF-8, fin de ligne \\n.

Les dessins sont de Goldwolf (DCS Reference Guide), utilisés avec son accord et hors licence AGPL du dépôt : voir
data/views/LICENSE.md. Bibliothèque standard seulement.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
VIEWS = os.path.join(DATA, 'views')
OUT = os.path.join(DATA, 'aircraft_views.json')


def build():
    with open(os.path.join(VIEWS, 'stations.json'), encoding='utf-8', newline='') as fh:
        table = json.load(fh)
    for tid, entry in table.items():
        path = entry.get('svg')
        if not isinstance(path, str):
            sys.exit('Pas de dessin pour %s' % tid)
        with open(os.path.join(DATA, path), encoding='utf-8', newline='') as fh:
            entry['svg'] = fh.read()
    return json.dumps(table, ensure_ascii=False, indent=1) + '\n'


def main():
    if len(sys.argv) != 1:
        sys.exit(__doc__)
    text = build()
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)
    print('%d types -> %s' % (json.loads(text).__len__(), os.path.normpath(OUT)))


if __name__ == '__main__':
    main()
