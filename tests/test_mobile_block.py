"""Garde du bloc du téléphone : une copie exacte dans chacun des quatre modules, rien de mph…/MPH… défini ailleurs ;
une copie altérée d'un caractère arrête le build (le build est lancé sur une copie de travail)."""
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def charger_build():
    spec = importlib.util.spec_from_file_location('build_mission_tools_t', ROOT / 'build_mission_tools.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


B = charger_build()
MODULES = [m['src'] for m in B.MODULES]


@pytest.mark.parametrize('src', MODULES)
def test_le_bloc_est_identique_dans_chaque_module(src):
    texte = (ROOT / src).read_text(encoding='utf-8')
    assert B.check_mobile_text(texte, src) is None


def test_une_copie_alteree_d_un_caractere_est_refusee():
    src = MODULES[0]
    texte = (ROOT / src).read_text(encoding='utf-8')
    debut = texte.index(B.MOBILE_BEGIN) + len(B.MOBILE_BEGIN) + 200
    altere = texte[:debut] + ('x' if texte[debut] != 'x' else 'y') + texte[debut + 1:]
    assert B.check_mobile_text(altere, src) is not None


def test_le_bloc_en_double_est_refuse():
    src = MODULES[0]
    texte = (ROOT / src).read_text(encoding='utf-8')
    assert B.check_mobile_text(texte + B.build_mobile_block(), src) is not None


@pytest.mark.parametrize('definition', [
    'function mphAutre() {}',
    'const mphAutre = 1;',
    'window.mph = {};',
    'let MPH_CSS = "";',
])
def test_une_definition_mph_hors_du_bloc_est_refusee(definition):
    src = MODULES[0]
    texte = (ROOT / src).read_text(encoding='utf-8')
    assert B.check_mobile_text(texte + '\n<script>' + definition + '</script>\n', src) is not None


def test_une_lecture_de_mph_hors_du_bloc_reste_permise():
    src = MODULES[0]
    texte = (ROOT / src).read_text(encoding='utf-8')
    assert B.check_mobile_text(texte + '\n<script>mph.refresh(); const x = mph.phone.matches;</script>\n', src) is None


def test_le_build_s_arrete_sur_une_copie_alteree(tmp_path):
    """Le build lui-même, sur une copie de travail : un caractère changé dans le bloc d'un module -> code 1, aucun fichier écrit."""
    copie = tmp_path / 'copie'
    shutil.copytree(ROOT, copie, ignore=shutil.ignore_patterns('.git', '__pycache__', 'dist', 'docs', '.pytest_cache'))
    mod = copie / MODULES[1]
    texte = mod.read_text(encoding='utf-8')
    i = texte.index(B.MOBILE_BEGIN) + len(B.MOBILE_BEGIN) + 300
    mod.write_text(texte[:i] + ('x' if texte[i] != 'x' else 'y') + texte[i + 1:], encoding='utf-8')
    p = subprocess.run([sys.executable, '-B', 'build_mission_tools.py'], cwd=str(copie), capture_output=True, text=True, encoding='utf-8')
    assert p.returncode == 1
    assert 'diffère de mobile_block.py' in p.stderr and 'build arrêté' in p.stderr
    assert not (copie / 'dist' / 'dcs_mission_tools.html').exists()
