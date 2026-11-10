#!/usr/bin/env python3
"""fixture_accents.py <demo_mission.miz> <out.miz>

Builds, from the demo mission, a test mission with difficult names: accents, Cyrillic, escaped quotes, `$&` and `$'`
(String.replace patterns), a backslash, markup that must stay plain text; and two joined entries with a non-ASCII name
(an image, a sound). Needs nothing but the Python standard library. The mission holds no real unit or person name."""
import re
import sys
import zipfile

src, dst = sys.argv[1], sys.argv[2]
zin = zipfile.ZipFile(src)
mission = zin.read('mission').decode('utf-8')
RENAME = {
    'Hind 1': 'Хинд «Été» $& 1',                 # player helicopter group (Loadout Editor, Comm Plan Editor)
    'Phantom 1': 'Phantom ÀÉÎÕÜ \\"Q\\" $\' 1',  # player aircraft: escaped quotes inside the Lua
    'Armor 1': 'Броня Été $& 1',                  # red ground group (Ground Unit Swapper)
    'SAM 2': 'SAM \\\\ Ŝ 2',                      # escaped backslash
    'Hind 2': 'Hind <i>2</i> &amp; <img src=x onerror=alert(1)>',  # markup: must stay text
    'Infantry 1': 'Infantry <b>1</b>',
}
n = 0
for a, b in RENAME.items():
    mission, k = re.subn(r'(\["name"\]\s*=\s*")' + re.escape(a), lambda m: m.group(1) + b, mission)
    n += k
print('names replaced:', n)
PNG = bytes.fromhex('89504e470d0a1a0a0000000d4948445200000001000000010806000000'
                    '1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082')
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
    for i in zin.infolist():
        data = mission.encode('utf-8') if i.filename == 'mission' else zin.read(i.filename)
        zout.writestr(i.filename, data)
    zout.writestr('l10n/DEFAULT/Карта été №1.png', PNG)
    zout.writestr('KNEEBOARD/IMAGES/planche à côté.png', PNG)
