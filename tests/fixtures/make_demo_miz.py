"""Generate a neutral demo .miz (Caucasus) for the Mission Tools README captures.
Usage: python3 -B make_demo_miz.py out.miz   (needs pydcs==1.0.0)
No real squadron, unit or person names."""
import sys, datetime, warnings
warnings.filterwarnings('ignore')
import dcs
from dcs.mission import Mission, StartType
from dcs.countries import USSR, USA
from dcs.helicopters import Mi_24P, Mi_8MT
from dcs.planes import F_4E_45MC
from dcs.mapping import Point
from dcs import vehicles as V
from dcs.terrain import Caucasus
from dcs.weather import Weather, Wind
from dcs.unit import Skill

out = sys.argv[1] if len(sys.argv) > 1 else 'demo.miz'
m = Mission(Caucasus())
m.start_time = datetime.datetime(2026, 6, 14, 6, 30)
red = m.coalition['red']; blue = m.coalition['blue']
red.add_country(USSR()); blue.add_country(USA())
ru, us = m.country('USSR'), m.country('USA')
ap = m.terrain.airports

def pick(ptype, pyl, *keys):
    d = getattr(ptype, 'Pylon%d' % pyl)
    for n, v in vars(d).items():
        if isinstance(v, tuple) and len(v) == 2 and all(k.lower() in n.lower() for k in keys):
            return v
    raise SystemExit('pylon %d %s not found: %s' % (pyl, ptype.id, keys))

def flight(country, name, typ, airport, n, client, freq, load, offset):
    g = m.flight_group(country, name, typ, airport, None, altitude=300, speed=0,
                       start_type=StartType.Cold, group_size=n)
    for i, u in enumerate(g.units):
        u.name = '%s-%d' % (name, i + 1)
        if client:
            u.set_client()
    g.set_frequency(freq)
    for pyl, key in load:
        g.load_pylon(pick(typ, pyl, *key), pyl)
    for u in g.units:
        u.fuel = typ.fuel_max * 0.8
    return g

# Mi-24P : two groups, two different loadouts
loadA = [(1, ('ataka', 'tandem')), (6, ('ataka', 'tandem')), (2, ('ub_32', 's_5ko')), (5, ('ub_32', 's_5ko')),
         (3, ('b_8v20a', 'om')), (4, ('b_8v20a', 'om'))]
loadB = [(1, ('shturm',)), (6, ('shturm',)), (2, ('b_8v20a', 'cm')), (5, ('b_8v20a', 'cm')),
         (3, ('ub_32', 's_5m')), (4, ('ub_32', 's_5m'))]
flight(ru, 'Hind 1', Mi_24P, ap['Kobuleti'], 2, True, 127.5, loadA, 0)
flight(ru, 'Hind 2', Mi_24P, ap['Kobuleti'], 2, True, 128.0, loadB, 0)
g = flight(ru, 'Hip 1', Mi_8MT, ap['Batumi'], 2, True, 130.0, [], 0)
# Mi-8MT: any rocket pod on its outer pylons
for pyl in (1, 2, 5, 6):
    g.load_pylon(pick(Mi_8MT, pyl, 'b_8v20a_cm'), pyl)
flight(us, 'Phantom 1', F_4E_45MC, ap['Senaki-Kolkhi'], 2, True, 305.0,
       [(2, ('aim_9p_sidewinder',)), (12, ('aim_9p_sidewinder',)), (1, ('3x_m117',)), (13, ('3x_m117',)), (6, ('aim_7f',)), (9, ('aim_7f',))], 0)

# ground groups
def gv(country, name, typ, x, y, n, hdg=0):
    g = m.vehicle_group(country, name, typ, Point(x, y, m.terrain), heading=hdg, group_size=n)
    return g
bx, by = ap['Kutaisi'].position.x, ap['Kutaisi'].position.y
specs = [
 (ru, 'Armor 1', V.Armor.T_72B, 0, 20000, 4), (ru, 'Armor 2', V.Armor.BMP_1, 1500, 20800, 4),
 (ru, 'AAA 1', V.AirDefence.ZSU_23_4_Shilka, -1500, 21000, 2), (ru, 'SAM 1', V.AirDefence.Kub_2P25_ln, 3000, 22000, 3),
 (ru, 'Artillery 1', V.Artillery.Grad_URAL, -3000, 23000, 3), (ru, 'Logistics 1', V.Unarmed.Ural_375, 4500, 20000, 3),
 (ru, 'Infantry 1', V.Infantry.Infantry_AK, 6000, 21500, 6),
 (us, 'Armor 3', V.Armor.M_1_Abrams, 0, -20000, 4), (us, 'Armor 4', V.Armor.M_2_Bradley, 1500, -20800, 4),
 (us, 'SAM 2', V.AirDefence.Hawk_ln, -1500, -21500, 3), (us, 'SHORAD 1', V.AirDefence.Roland_ADS, 3000, -22000, 2),
 (us, 'Artillery 2', V.Artillery.M_109, -3000, -23000, 3), (us, 'Logistics 2', V.Unarmed.M_818, 4500, -20000, 3),
 (us, 'Infantry 2', V.Infantry.Soldier_M4, 6000, -21500, 6),
]
skills = [Skill.Average, Skill.Good, Skill.High, Skill.Excellent]
for i, (c, n, t, dx, dy, k) in enumerate(specs):
    g = gv(c, n, t, bx + dx, by + dy, k, 90)
    for u in g.units:
        u.skill = skills[i % 4]

# weather
w = m.weather
w.name = 'Demo weather'
w.wind_at_ground = Wind(250, 4)
w.wind_at_2000 = Wind(260, 9)
w.wind_at_8000 = Wind(270, 18)
w.qnh = 758
w.season_temperature = 22
w.turbulence_at_ground = 3
w.visibility_distance = 60000
from dcs.cloud_presets import Clouds
w.clouds_preset = Clouds.Broken4.value      # Preset16
w.clouds_base = 1800
m.save(out)
print('saved', out)
