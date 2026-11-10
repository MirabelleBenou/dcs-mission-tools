"""Exécute les définitions Lua des appareils de DCS (bouchons pour l'API du jeu) et relève, par type, les règles
entre stations : `required` et `forbidden` de chaque emport. Usage : extrait_regles.py <racine CoreMods/aircraft> <sortie.json>"""
import sys, os, json, glob
from lupa import LuaRuntime
STUBS = r'''
local D
local mt = {}
D = setmetatable({}, mt)
mt.__index = function() return D end
mt.__newindex = function() end
mt.__call = function() return D end
for _,k in ipairs({"__add","__sub","__mul","__div","__mod","__pow","__unm"}) do mt[k] = function() return 0 end end
mt.__concat = function() return "" end
mt.__lt = function() return false end
mt.__le = function() return false end
mt.__len = function() return 0 end
CAPT = {}
function _(s) return s end
function pylon(n, t, x, y, z, params, launchers)
  return {Number = n, DisplayName = (type(params)=="table" and params.DisplayName) or nil, Launchers = launchers or {}}
end
function make_payload_rules_list(stations, clsids)
  local r = {}
  for _, s in ipairs(stations) do r[#r+1] = {station = s, loadout = clsids} end
  return r
end
function add_aircraft(t) CAPT[#CAPT+1] = t; return t end
function dofile() return D end
function loadfile() return function() return D end end
function require() return D end
current_mod_path = ""
setmetatable(_G, {__index = function(_, k) return D end})
'''
def tolist(lt):
    if lt is None: return []
    try: return [lt[i] for i in range(1, len(lt)+1)]
    except Exception: return []
def rules(lst):
    out = []
    for r in tolist(lst):
        try:
            st = r['station']; lo = [str(x) for x in tolist(r['loadout'])] if r['loadout'] is not None else None
            out.append({'st': int(st) if st is not None else None, 'loadout': lo})
        except Exception: pass
    return out
def run(dirpath, files):
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(STUBS)
    res = {}
    for f in files:
        try:
            src = open(f, encoding='utf-8', errors='replace').read()
            r = lua.execute(src)
        except Exception as e:
            print('  ERREUR', os.path.basename(f), str(e)[:120]); continue
    capt = lua.globals().CAPT
    for t in tolist(capt):
        try: name = t['Name']; py = t['Pylons']
        except Exception: continue
        if not isinstance(name, str) or py is None: continue
        rows = []
        for p in tolist(py):
            try: n = p['Number']; L = p['Launchers']
            except Exception: continue
            for l in tolist(L):
                try: c = l['CLSID']
                except Exception: continue
                req = rules(l['required']) if l['required'] is not None else []
                frb = rules(l['forbidden']) if l['forbidden'] is not None else []
                if req or frb: rows.append({'st': int(n), 'clsid': str(c), 'required': req, 'forbidden': frb})
        res[name] = rows
    return res
root, out = sys.argv[1], sys.argv[2]
ORDER = {'A-10': ['A-10A.lua', 'A-10C.lua', 'A-10C_2.lua'], 'F14/Entry': ['F-14B.lua', 'F-14A.lua'],
         'F-5E': ['F-5E.lua', 'F-5E-3.lua', 'F-5E-3_FC.lua'], 'Mirage-F1': ['Payloads.lua', 'Mirage-F1.lua', 'Mirage-F1B.lua', 'Mirage-F1C.lua'],
         'A-6E/Entry': ['Pylons.lua', 'A-6E.lua'], 'FA-18C': ['FA-18C.lua', 'FA-18C_hornet.lua', 'FA-18A.lua']}
allres = {}
dirs = sorted({os.path.dirname(p) for p in glob.glob(os.path.join(root, '**', '*.lua'), recursive=True)})
for d in dirs:
    rel = os.path.relpath(d, root)
    files = [os.path.join(d, f) for f in ORDER.get(rel, sorted(os.listdir(d))) if f.endswith('.lua') and os.path.exists(os.path.join(d, f))]
    r = run(d, files)
    print(rel, '->', {k: len(v) for k, v in r.items()})
    allres.update(r)
json.dump(allres, open(out, 'w'), indent=1, ensure_ascii=False)
