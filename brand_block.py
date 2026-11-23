#!/usr/bin/env python3
"""Bloc « MARQUE » — une seule source pour les quatre outils de Mission Tools (pas pour le shell).

Rend le texte JavaScript du bloc : l'insigne de la famille « Squadron Ready Room » dans l'outil. Le pictogramme est lu dans
assets/brand/pictogramme.svg (chemin relatif au dossier de ce script) et intégré en data:image/svg+xml;base64. Fichier absent ou
illisible : build_block() lève une exception claire (le build la rend en [ERREUR], code 1, avant toute écriture).
À son exécution, le bloc pose une seule fois (idempotent : rien de plus s'il a déjà posé) :
  - une feuille de style à lui (<style data-mtb-brand>) ;
  - l'en-tête : le pictogramme (<img class="mtb-picto">, 22 × 22) en premier enfant de #app-header .header-logo, avant le sigle,
    qui garde sa police, sa taille et sa couleur ;
  - l'écran vide : la ligne de signature (<div class="mtb-signature">, pictogramme de 18 × 18 et « Squadron Ready Room family »,
    nom de marque identique en FR et en EN, sans clé i18n) juste avant le premier .credits du document.
Un élément absent (pas de .header-logo, pas de .credits) : le bloc ne pose que ce qu'il peut, sans erreur.
Aucun point d'entrée public.
Le bloc est identique à l'octet dans les quatre modules : build_mission_tools.py le garde (build en code 1 sinon).

Usage (par le build) : from brand_block import build_block ; texte = build_block()
"""
import base64
import os

BLOCK_BEGIN = '/* ===== MARQUE (INSIGNE DE LA FAMILLE) ===== */'
BLOCK_END = '/* ===== FIN DE LA MARQUE ===== */'

PICTO_PATH = os.path.join('assets', 'brand', 'pictogramme.svg')

_JS = r"""
/* Marque : le pictogramme de la famille avant le sigle de l'en-tête, la ligne de signature au-dessus des crédits de l'écran vide. */
(function () {
  const SRC = '__PICTO__';
  const CSS = `
#app-header .header-logo { display: inline-flex; align-items: center; gap: 8px; }
.mtb-picto { flex: 0 0 auto; }
.mtb-signature { text-align: center; font: 500 12px var(--font-ui); letter-spacing: 2.5px; text-transform: uppercase; color: #C9A64A; margin: 0 0 10px; }
.mtb-signature img { vertical-align: -4px; margin-right: 8px; }
`;
  function mark() {
    if (!document.querySelector('style[data-mtb-brand]')) {
      const st = document.createElement('style');
      st.setAttribute('data-mtb-brand', '');
      st.textContent = CSS;
      document.head.appendChild(st);
    }
    const logo = document.querySelector('#app-header .header-logo');
    if (logo && !logo.querySelector(':scope > .mtb-picto')) {
      const img = document.createElement('img');
      img.className = 'mtb-picto';
      img.src = SRC;
      img.alt = '';
      img.width = 22;
      img.height = 22;
      logo.insertBefore(img, logo.firstChild);
    }
    const credits = document.querySelector('.credits');
    if (credits && credits.parentNode && !document.querySelector('.mtb-signature')) {
      const sig = document.createElement('div');
      sig.className = 'mtb-signature';
      const img = document.createElement('img');
      img.src = SRC;
      img.alt = '';
      img.width = 18;
      img.height = 18;
      sig.appendChild(img);
      sig.appendChild(document.createTextNode('Squadron Ready Room family'));
      credits.parentNode.insertBefore(sig, credits);
    }
  }
  if (document.body) mark(); else document.addEventListener('DOMContentLoaded', mark);
})();
"""


def build_block():
    """Le texte du bloc, délimité par ses deux commentaires, avec un saut de ligne final."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), PICTO_PATH)
    try:
        with open(path, 'rb') as fh:
            data = fh.read()
    except OSError as exc:
        raise RuntimeError(f'Pictogramme de la marque illisible ({PICTO_PATH} : {exc})') from exc
    if not data:
        raise RuntimeError(f'Pictogramme de la marque vide ({PICTO_PATH})')
    uri = 'data:image/svg+xml;base64,' + base64.b64encode(data).decode('ascii')
    return BLOCK_BEGIN + _JS.replace('__PICTO__', uri) + BLOCK_END + '\n'
