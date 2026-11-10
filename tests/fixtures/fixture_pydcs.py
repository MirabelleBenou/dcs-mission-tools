#!/usr/bin/env python3
"""fixture_pydcs.py <out.miz>

A mission written by pydcs 1.0.0 (the format without a trailing comma, the one of the generators built on it): Caucasus,
two red countries (Russia, Ukraine) each with a group of player Mi-24P, an AI Russian Su-25T group, a blue group (USA,
player F-16C), ground units of both sides, default dynamic weather. No real unit or person name.

Needs: pip install pydcs==1.0.0"""
import sys
import warnings

warnings.filterwarnings('ignore')
import dcs  # noqa: E402
from dcs import helicopters, planes, vehicles  # noqa: E402
from dcs.terrain import Caucasus  # noqa: E402

m = dcs.Mission(terrain=Caucasus())
ru, ua, us = m.country('Russia'), m.country('Ukraine'), m.country('USA')
kutaisi = m.terrain.airports['Kutaisi']
senaki = m.terrain.airports['Senaki-Kolkhi']
krym = m.terrain.airports['Krymsk']
g1 = m.flight_group_inflight(ru, 'Ми-24 «Été» $& 1', helicopters.Mi_24P, kutaisi.position.point_from_heading(0, 5000), 300, group_size=2)
for u in g1.units:
    u.set_client()
g2 = m.flight_group_inflight(ua, 'Hind UA 1', helicopters.Mi_24P, senaki.position.point_from_heading(0, 5000), 300, group_size=2)
for u in g2.units:
    u.set_client()
m.flight_group_inflight(ru, 'Frogfoot 1', planes.Su_25T, krym.position.point_from_heading(90, 9000), 3000, group_size=2)
g4 = m.flight_group_inflight(us, 'Viper 1', planes.F_16C_50, senaki.position.point_from_heading(180, 20000), 5000, group_size=2)
for u in g4.units:
    u.set_client()
m.vehicle_group(ru, 'Armor RU', vehicles.Armor.T_72B, kutaisi.position.point_from_heading(45, 8000), group_size=4)
m.vehicle_group(us, 'Armor US', vehicles.Armor.M_1_Abrams, senaki.position.point_from_heading(45, 8000), group_size=4)
m.save(sys.argv[1])
print('written', sys.argv[1])
