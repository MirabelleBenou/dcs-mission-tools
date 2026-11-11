#!/usr/bin/env python3
"""Bloc « GARDE DU MODULE SEUL » — une seule source pour les quatre outils de Mission Tools.

Depuis la v2, un outil ne s'ouvre plus seul : il vit dans Mission Tools (le fichier global autoportant dcs_mission_tools.html,
ou la version en ligne). Ce bloc rend le texte d'un <script> classique, autonome (aucune dépendance, pur ASCII), que chaque module
pose comme PREMIER élément de son <head> (juste après <meta charset>), sous la forme

    <script data-lang-key="<KEY_LANG du module>">
    ...texte du bloc...
    </script>

Contrat :
  - Page dans une iframe (window.parent !== window), c'est-à-dire l'outil ouvert par le shell : le bloc ne fait rien.
  - Page seule : le bloc appelle window.stop() (le reste du document n'est jamais lu : aucun script du module ne s'exécute,
    aucun écouteur, aucun élément de l'outil), crée le <body> s'il n'existe pas, et y pose une seule ligne <p> : le texte
    « shell.only » de la langue, dont le texte « shell.online » (première occurrence) devient un lien vers la version en ligne.
  - Langue : la règle de initLang() des modules. La valeur fr ou en mémorisée sous la clé de langue du module (localStorage, lue
    dans un try ; la clé est l'attribut data-lang-key de la balise, lu par document.currentScript), sinon fr si navigator.language
    commence par fr, sinon en. Le bloc n'écrit rien dans le stockage.
  - Style en ligne minimal (color-scheme clair et sombre, aucune feuille du module n'est chargée), sans défilement horizontal.
Effet de bord connu : window.stop() empêche l'évènement load d'une page seule (document.readyState vaut complete).

Les textes (FR / EN), identiques pour les quatre modules :
  shell.only    Cet outil fait partie de Mission Tools : ouvrez dcs_mission_tools.html, ou la version en ligne.
                This tool is part of Mission Tools: open dcs_mission_tools.html, or the online version.
  shell.online  la version en ligne  /  the online version
Adresse du lien : https://mirabellebenou.github.io/dcs-mission-tools/

Le bloc est identique à l'octet dans les quatre modules, et absent du shell : build_mission_tools.py le garde (build en code 1
sinon).

Usage (par le build) : from shell_only_block import build_block ; texte = build_block()
"""

BLOCK_BEGIN = '/* ===== GARDE DU MODULE SEUL ===== */'
BLOCK_END = '/* ===== FIN DE LA GARDE ===== */'

_JS = r"""
(function () {
  if (window.parent !== window) return;
  var TXT = {
    fr: { only: 'Cet outil fait partie de Mission Tools : ouvrez dcs_mission_tools.html, ou la version en ligne.', online: 'la version en ligne' },
    en: { only: 'This tool is part of Mission Tools: open dcs_mission_tools.html, or the online version.', online: 'the online version' }
  };
  var HREF = 'https://mirabellebenou.github.io/dcs-mission-tools/';
  var me = document.currentScript;
  var key = me && me.getAttribute('data-lang-key');
  var lang = null;
  try { lang = localStorage.getItem(key); } catch (e) {}
  if (lang !== 'fr' && lang !== 'en') lang = (navigator.language || 'fr').toLowerCase().indexOf('fr') === 0 ? 'fr' : 'en';
  try { window.stop(); } catch (e) {}
  var root = document.documentElement;
  root.lang = lang;
  root.style.colorScheme = 'light dark';
  var body = document.body;
  if (!body) { body = document.createElement('body'); root.appendChild(body); }
  body.textContent = '';
  body.style.margin = '0';
  var p = document.createElement('p');
  p.style.cssText = 'margin:0;padding:16px 20px;font:14px/1.5 system-ui,sans-serif;overflow-wrap:anywhere';
  var t = TXT[lang], i = t.only.indexOf(t.online);
  if (i < 0) p.textContent = t.only;
  else {
    var a = document.createElement('a');
    a.href = HREF;
    a.textContent = t.online;
    p.appendChild(document.createTextNode(t.only.slice(0, i)));
    p.appendChild(a);
    p.appendChild(document.createTextNode(t.only.slice(i + t.online.length)));
  }
  body.appendChild(p);
})();
"""


def build_block():
    """Le texte du bloc, délimité par ses deux commentaires, avec un saut de ligne final."""
    return BLOCK_BEGIN + _JS + BLOCK_END + '\n'
