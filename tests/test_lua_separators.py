#!/usr/bin/env python3
"""Lua table separator bench - run from the repository root:  python3 -B tests/test_lua_separators.py

For each of the four modules (modules/dcs_*.html), takes its DCS_TOKENIZER and the parser block (DCS_PARSER and
retokenizeSafety), runs them under Node, and checks on the mission samples written below that the parser follows the grammar
of Lua tables. The samples are: one in the format of the DCS mission editor (a comma after every field, "-- end of [n]"),
one in the pydcs format (no comma after the last field of a table), one whose fields are separated by `;`, and one that mixes
`,` and `;`; each of them is also run with CRLF line ends. For each sample:
  (a) the sample is accepted, by the parser and by retokenizeSafety;
  (b) the sample deprived of a single separator (one case per separator) is refused if the separator stood between two fields,
      accepted if it was the last one of its table;
  (c) a doubled separator (one case per separator) and a separator right after a "{" (one case per opening brace and per
      separator character that the sample uses) are refused.
Needs nothing but Python 3 and Node (no network). Output: one line "[OK] <module> - <sample>: <n> cases" per module and per
sample; at the first wrong case, a line "[FAIL] ..." that names it (module, sample, line), and exit code 1."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULES = ['dcs_comm_plan_editor', 'dcs_ground_unit_swapper', 'dcs_weather_editor', 'dcs_loadout_editor']

# The markers of the parser block (parser_block.py). A module that lacks them (an older copy) is read its own way: the two
# definitions are taken directly.
BLOCK_BEGIN = '/* ===== PARSEUR DE LA SUITE ===== */'
BLOCK_END = '/* ===== FIN DU PARSEUR ===== */'

# -- Sample in the format of the DCS mission editor: a comma after every field, an end-of-entry comment ------------------------
SAMPLE_DCS = r'''mission =
{
	["version"] = 19, -- a comment, with a comma
	["sortie"] = "Flight, then back ; end",
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

# -- Sample in the pydcs format: no comma after the last field of a table, no comments ------------------------------------------
SAMPLE_PYDCS = r'''mission=
{
	["version"]=19,
	["sortie"]="Flight, then back ; end",
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

# -- Sample whose fields are separated by `;` (a legal Lua separator), with a trailing `;` in some tables and comments ----------
SAMPLE_SEMI = r'''mission =
{
	["version"] = 19; -- a comment, with a comma, and a semicolon
	["sortie"] = "Flight, then back ; end";
	["forcedOptions"] =
	{
	}; -- end of ["forcedOptions"]
	["trig"] =
	{
		["actions"] =
		{
			[1] = "a_do_script(\"x, y\")";
			[2] = "a_out_text"
		}; -- end of ["actions"]
		["flags"] =
		{
			[1] = true;
			[2] = false;
		} -- end of ["flags"]
	}; -- end of ["trig"]
	["coalition"] =
	{
		["red"] =
		{
			["country"] =
			{
				[1] =
				{
					["id"] = 0;
					["name"] = "Russia";
					["position"] =
					{
						["x"] = -291014.5;
						["y"] = 6.17e5
					}
				}
			}
		}
	}
}
'''

# -- Sample that mixes `,` and `;`: both between fields of one table, either as the trailing separator ----------------------------
SAMPLE_MIXED = r'''mission =
{
	["version"] = 19, -- a comment, with a comma, and a semicolon
	["sortie"] = "Flight, then back ; end";
	["forcedOptions"] =
	{
	}, -- end of ["forcedOptions"]
	["trig"] =
	{
		["actions"] =
		{
			[1] = "a_do_script(\"x, y\")";
			[2] = "a_out_text",
			[3] = "a_out_sound";
		}; -- end of ["actions"]
		["flags"] =
		{
			[1] = true,
			[2] = false;
			[3] = true
		} -- end of ["flags"]
	}; -- end of ["trig"]
	["coalition"] =
	{
		["red"] =
		{
			["country"] =
			{
				[1] =
				{
					["id"] = 0;
					["name"] = "Russia",
					["position"] =
					{
						["x"] = -291014.5;
						["y"] = 6.17e5,
					}; -- end of ["position"]
				}, -- end of [1]
			}
		};
	}
}
'''


def crlf(text):
    return text.replace('\n', '\r\n')


# (label, text, the separator characters inserted right after a "{")
SAMPLES = []
for _label, _text, _seps in [('DCS mission editor format', SAMPLE_DCS, ','),
                             ('pydcs format', SAMPLE_PYDCS, ','),
                             ('semicolon separators', SAMPLE_SEMI, ';'),
                             ('mixed , and ; separators', SAMPLE_MIXED, ',;')]:
    SAMPLES.append((_label, _text, _seps))
    SAMPLES.append((_label + ', CRLF line ends', crlf(_text), _seps))


def extract_between(text, start, end_marker, label):
    i = text.find(start)
    if i < 0:
        raise SystemExit('[ERROR] %s not found' % label)
    j = text.find(end_marker, i)
    if j < 0:
        raise SystemExit('[ERROR] end of %s not found' % label)
    return text[i:j + len(end_marker)]


def js_for(module):
    """The JavaScript to try for a module: its DCS_TOKENIZER, then the parser block."""
    with open(os.path.join(ROOT, 'modules', module + '.html'), encoding='utf-8') as fh:
        html = fh.read()
    tok = extract_between(html, 'const DCS_TOKENIZER = (() => {', '\n})();', 'DCS_TOKENIZER of ' + module)
    if BLOCK_BEGIN in html:
        block = extract_between(html, BLOCK_BEGIN, BLOCK_END, 'the parser block of ' + module)
    else:
        parser = extract_between(html, 'const DCS_PARSER = (() => {', '\n})();', 'DCS_PARSER of ' + module)
        retok = extract_between(html, 'function retokenizeSafety', '\n}\n', 'retokenizeSafety of ' + module)
        block = parser + '\n' + retok
    return tok + '\n' + block + '\n'


DRIVER = r'''
const cases = JSON.parse(require('fs').readFileSync(0, 'utf8'));
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
        raise SystemExit('[ERROR] Node failed: ' + p.stderr.decode('utf-8', 'replace')[:400])
    return json.loads(p.stdout.decode('utf-8'))


def scan(text):
    """Reads a Lua table text with no parser's help: returns (separators, opening braces). A separator is
    (position, last) where `last` says that it is followed by the "}" of its table; a brace is its position."""
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
            while j < n:                      # the character that counts after the separator
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


def cases_of(text, brace_seps):
    """The cases of a sample: (text, expected_accepted, description, line)."""
    seps, braces = scan(text)
    cases = [(text, True, 'whole sample', 0)]
    for pos, last in seps:
        ln = line_of(text, pos)
        cases.append((text[:pos] + text[pos + 1:], last,
                      'separator removed (%s)' % ('last of its table: accepted' if last else 'between two fields: refused'), ln))
    for pos, last in seps:
        cases.append((text[:pos + 1] + text[pos] + text[pos + 1:], False, 'separator doubled: refused', line_of(text, pos)))
    for pos in braces:
        for sep in brace_seps:
            cases.append((text[:pos + 1] + sep + text[pos + 1:], False, 'separator "%s" after "{": refused' % sep, line_of(text, pos)))
    return cases


def main():
    if shutil.which('node') is None:
        print('[ERROR] Node was not found (the bench needs Node and Python 3, nothing else).')
        return 2
    with tempfile.TemporaryDirectory() as tmp:
        for module in MODULES:
            script = os.path.join(tmp, module + '.js')
            with open(script, 'w', encoding='utf-8') as fh:
                fh.write(js_for(module) + DRIVER)
            for label, text, brace_seps in SAMPLES:
                cases = cases_of(text, brace_seps)
                res = run_node(script, [c[0] for c in cases])
                for (_, want, what, ln), r in zip(cases, res):
                    for who, got in (('parser', r['parse']), ('retokenizeSafety', r['safety'])):
                        if got != want:
                            print('[FAIL] %s - %s: %s, line %s: %s %s instead of %s'
                                  % (module, label, what, ln or '-', who, 'accepted' if got else 'refused', 'accepting' if want else 'refusing'))
                            return 1
                print('[OK] %s - %s: %d cases' % (module, label, len(cases)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
