#!/usr/bin/env python3
"""Génère data/aircraft_masses.json (type DCS -> masse à vide et masse maximale, kg) depuis un relevé du jeu.

Usage :
    python3 -I tools/gen_aircraft_masses.py <relevé>

Source : un relevé fait dans DCS World par un script de mission qui appelle Unit.getDescByName(type) pour chaque type de
data/aircraft_limits.json. Une ligne par type :
    type;massEmpty;massMax;fuelMassMax
en kg, flottants du jeu (8866.2001953125) ; `nil` pour une valeur absente ; dernière ligne `FIN;<n>;<n>`, où <n> est le
nombre de lignes de types. La quatrième colonne (carburant) est lue et ignorée : le carburant vient de aircraft_limits.json.

Règles :
- empty = massEmpty, max = massMax, arrondis à l'entier le plus proche, une moitié vers le haut (math.floor(x + 0.5)) ;
- un type dont l'une des deux masses est `nil` est omis (l'éditeur n'a alors pas d'estimation) ;
- le script s'arrête (message, code de sortie 1, rien d'écrit) si la dernière ligne n'est pas `FIN;<n>;<n>` avec <n> égal au
  nombre de lignes de types, si une ligne n'a pas quatre champs, si une masse n'est ni un nombre ni `nil`, ou si un type
  figure deux fois.

Sortie : data/aircraft_masses.json
    {
     "<type>": {"empty": <kg>, "max": <kg>},
     ...
    }
une ligne par type, clés triées, fin de ligne \\n après l'accolade fermante. Deux passages sur le même relevé donnent les
mêmes octets. Bibliothèque standard seulement.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'data', 'aircraft_masses.json')


def fail(msg):
    sys.stderr.write('gen_aircraft_masses: ' + msg + '\n')
    sys.exit(1)


def mass(txt, line_no):
    """Un nombre (flottant du jeu), ou None pour `nil`."""
    if txt == 'nil':
        return None
    try:
        v = float(txt)
    except ValueError:
        fail('ligne %d : « %s » n\'est ni un nombre ni nil' % (line_no, txt))
    if math.isnan(v) or math.isinf(v):
        fail('ligne %d : « %s » n\'est pas un nombre fini' % (line_no, txt))
    return v


def parse(path):
    with open(path, encoding='utf-8') as f:
        lines = [l.strip() for l in f.read().splitlines()]
    while lines and not lines[-1]:
        lines.pop()
    if not lines:
        fail('relevé vide')
    parts = lines[-1].split(';')
    types = lines[:-1]
    if len(parts) != 3 or parts[0] != 'FIN' or parts[1] != parts[2] or not parts[1].isdigit():
        fail('la dernière ligne n\'est pas FIN;<n>;<n>')
    if int(parts[1]) != len(types):
        fail('FIN annonce %s types, le relevé en compte %d' % (parts[1], len(types)))
    out, seen = {}, set()
    for i, l in enumerate(types, 1):
        f = l.split(';')
        if len(f) != 4:
            fail('ligne %d : %d champs au lieu de 4' % (i, len(f)))
        t = f[0]
        if not t:
            fail('ligne %d : type vide' % i)
        if t in seen:
            fail('ligne %d : le type %s figure deux fois' % (i, t))
        seen.add(t)
        e, m = mass(f[1], i), mass(f[2], i)
        fuel = f[3]
        if fuel != 'nil':
            mass(fuel, i)
        if e is None or m is None:
            continue
        out[t] = {'empty': int(math.floor(e + 0.5)), 'max': int(math.floor(m + 0.5))}
    return out


def main():
    if len(sys.argv) != 2:
        fail('usage : python3 -I tools/gen_aircraft_masses.py <relevé>')
    d = parse(sys.argv[1])
    body = ',\n'.join(' ' + json.dumps(t) + ': ' + json.dumps(d[t]) for t in sorted(d))
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write('{\n' + body + '\n}\n')
    print('%d types écrits dans data/aircraft_masses.json' % len(d))


if __name__ == '__main__':
    main()
