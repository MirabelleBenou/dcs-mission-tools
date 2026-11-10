#!/usr/bin/env python3
"""Banc des séparateurs de tables Lua — à lancer depuis la racine du dépôt :  python3 -B tests/test_lua_separators.py

Pour chacun des quatre modules (modules/dcs_*.html), prend son DCS_TOKENIZER et le bloc du parseur (DCS_PARSER et
retokenizeSafety), les fait tourner sous Node, et vérifie sur deux échantillons de mission écrits ci-dessous — l'un au format
de l'éditeur de DCS (une virgule après chaque champ, « -- end of [n] »), l'autre au format de pydcs (aucune virgule après
le dernier champ d'une table) — que le parseur suit la grammaire des tables de Lua :
  (a) l'échantillon est accepté, par le parseur et par retokenizeSafety ;
  (b) l'échantillon privé d'un seul séparateur (un cas par séparateur) est refusé si le séparateur était entre deux champs,
      accepté s'il était le dernier de sa table ;
  (c) un séparateur doublé (un cas par séparateur) et un séparateur juste après une « { » (un cas par accolade ouvrante)
      sont refusés.
Sans réseau, avec Python 3 et Node seulement. Sortie : une ligne « [OK] <module> — <échantillon> : <n> cas » par module et par
échantillon ; au premier cas faux, une ligne « [ÉCHEC] … » qui le nomme (module, échantillon, ligne), et le code de sortie 1."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULES = ['dcs_comm_plan_editor', 'dcs_ground_unit_swapper', 'dcs_weather_editor', 'dcs_loadout_editor']

# Les marqueurs du bloc du parseur (parser_block.py). Un module qui n'a pas ces marqueurs (une copie plus ancienne) est lu à sa
# manière : on y prend directement les deux définitions.
BLOCK_BEGIN = '/* ===== PARSEUR DE LA SUITE ===== */'
BLOCK_END = '/* ===== FIN DU PARSEUR ===== */'

# ── Échantillon au format de l'éditeur de DCS : une virgule après chaque champ, un commentaire de fin d'entrée ────────────
SAMPLE_DCS = r'''mission =
{
	["version"] = 19, -- un commentaire, avec une virgule
	["sortie"] = "Vol, puis retour ; fin",
	["forcedOptions"] =
	{
	}, -- end of ["forcedOptions"]
	["trig"] =
	{
		["actions"] =
		{
			[1] = "a_do_script(\"x, y\")",
			[2] = "a_out_text",
		}, -- end of ["actions"]
		["flags"] =
		{
			[1] = true,
			[2] = false,
		}, -- end of ["flags"]
	}, -- end of ["trig"]
	["coalition"] =
	{
		["red"] =
		{
			["country"] =
			{
				[1] =
				{
					["id"] = 0,
					["name"] = "Russia",
					["position"] =
					{
						["x"] = -291014.5,
						["y"] = 6.17e5,
					}, -- end of ["position"]
				}, -- end of [1]
			}, -- end of ["country"]
		}, -- end of ["red"]
	}, -- end of ["coalition"]
} -- end of mission
'''

# ── Échantillon au format de pydcs : aucune virgule après le dernier champ d'une table, pas de commentaires ────────────────
SAMPLE_PYDCS = r'''mission=
{
	["version"]=19,
	["sortie"]="Vol, puis retour ; fin",
	["forcedOptions"]=
	{
	},
	["trig"]=
	{
		["actions"]=
		{
			[1]="a_do_script(\"x, y\")",
			[2]="a_out_text"
		},
		["flags"]=
		{
			[1]=true,
			[2]=false
		}
	},
	["coalition"]=
	{
		["red"]=
		{
			["country"]=
			{
				[1]=
				{
					["id"]=0,
					["name"]="Russia",
					["position"]=
					{
						["x"]=-291014.5,
						["y"]=6.17e5
					}
				}
			}
		}
	}
}
'''

SAMPLES = [('format de l\'éditeur de DCS', SAMPLE_DCS), ('format pydcs', SAMPLE_PYDCS)]


def extract_between(text, start, end_marker, label):
    i = text.find(start)
    if i < 0:
        raise SystemExit('[ERREUR] %s introuvable' % label)
    j = text.find(end_marker, i)
    if j < 0:
        raise SystemExit('[ERREUR] fin de %s introuvable' % label)
    return text[i:j + len(end_marker)]


def js_for(module):
    """Le JavaScript du module à essayer : son DCS_TOKENIZER, puis le bloc du parseur."""
    with open(os.path.join(ROOT, 'modules', module + '.html'), encoding='utf-8') as fh:
        html = fh.read()
    tok = extract_between(html, 'const DCS_TOKENIZER = (() => {', '\n})();', 'DCS_TOKENIZER de ' + module)
    if BLOCK_BEGIN in html:
        block = extract_between(html, BLOCK_BEGIN, BLOCK_END, 'le bloc du parseur de ' + module)
    else:
        parser = extract_between(html, 'const DCS_PARSER = (() => {', '\n})();', 'DCS_PARSER de ' + module)
        retok = extract_between(html, 'function retokenizeSafety', '\n}\n', 'retokenizeSafety de ' + module)
        block = parser + '\n' + retok
    return tok + '\n' + block + '\n'


DRIVER = r'''
const cases = JSON.parse(require('fs').readFileSync(0, 'utf8'));
console.log = () => {};
const out = cases.map(text => {
  const r = {};
  try { DCS_PARSER.parse(DCS_TOKENIZER.tokenize(text).tokens); r.parse = true; } catch (e) { r.parse = false; r.parseErr = String(e.message || e); }
  try { retokenizeSafety(text); r.safety = true; } catch (e) { r.safety = false; r.safetyErr = String(e.message || e); }
  return r;
});
process.stdout.write(JSON.stringify(out));
'''


def run_node(script_path, texts):
    p = subprocess.run(['node', script_path], input=json.dumps(texts).encode('utf-8'), capture_output=True)
    if p.returncode != 0:
        raise SystemExit('[ERREUR] Node a échoué : ' + p.stderr.decode('utf-8', 'replace')[:400])
    return json.loads(p.stdout.decode('utf-8'))


def scan(text):
    """Lit un texte Lua de table, sans l'aide d'aucun parseur : rend (séparateurs, accolades ouvrantes). Un séparateur :
    (position, dernier) où `dernier` dit qu'il est suivi du « } » de sa table ; une accolade : sa position."""
    seps, braces = [], []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == '-' and text[i:i + 2] == '--':
            while i < n and text[i] != '\n':
                i += 1
        elif c == '"':
            i += 1
            while i < n and text[i] != '"':
                i += 2 if text[i] == '\\' else 1
            i += 1
        elif c == '{':
            braces.append(i)
            i += 1
        elif c in ',;':
            j = i + 1
            while j < n:                      # le caractère qui compte après le séparateur
                if text[j] in ' \t\r\n':
                    j += 1
                elif text[j:j + 2] == '--':
                    while j < n and text[j] != '\n':
                        j += 1
                else:
                    break
            seps.append((i, j < n and text[j] == '}'))
            i += 1
        else:
            i += 1
    return seps, braces


def line_of(text, pos):
    return text.count('\n', 0, pos) + 1


def cases_of(text):
    """Les cas d'un échantillon : (texte, attendu_accepté, description, ligne)."""
    seps, braces = scan(text)
    cases = [(text, True, 'échantillon entier', 0)]
    for pos, last in seps:
        ln = line_of(text, pos)
        cases.append((text[:pos] + text[pos + 1:], last,
                      'séparateur retiré (%s)' % ('dernier de sa table : accepté' if last else 'entre deux champs : refusé'), ln))
    for pos, last in seps:
        cases.append((text[:pos + 1] + text[pos] + text[pos + 1:], False, 'séparateur doublé : refusé', line_of(text, pos)))
    for pos in braces:
        cases.append((text[:pos + 1] + ',' + text[pos + 1:], False, 'séparateur après « { » : refusé', line_of(text, pos)))
    return cases


def main():
    if shutil.which('node') is None:
        print('[ERREUR] Node est introuvable (le banc a besoin de Node et de Python 3, rien d\'autre).')
        return 2
    with tempfile.TemporaryDirectory() as tmp:
        for module in MODULES:
            script = os.path.join(tmp, module + '.js')
            with open(script, 'w', encoding='utf-8') as fh:
                fh.write(js_for(module) + DRIVER)
            for label, text in SAMPLES:
                cases = cases_of(text)
                res = run_node(script, [c[0] for c in cases])
                for (_, want, what, ln), r in zip(cases, res):
                    for who, got in (('parseur', r['parse']), ('retokenizeSafety', r['safety'])):
                        if got != want:
                            print('[ÉCHEC] %s — %s : %s, ligne %s : %s a %s au lieu de %s'
                                  % (module, label, what, ln or '-', who, 'accepté' if got else 'refusé', 'accepter' if want else 'refuser'))
                            return 1
                print('[OK] %s — %s : %d cas' % (module, label, len(cases)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
