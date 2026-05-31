#!/usr/bin/env python3
"""
build_mission_tools.py — DCS Mission Tools v1.0.0
Produit dcs_mission_tools_final.html (fichier autonome, single-file).

Usage : python3 build_mission_tools.py
Sorties : ./dist/dcs_mission_tools_final.html

Sources modules (à placer à côté de ce script) :
  dcs_comm_plan_editor_b.html
  dcs_ground_unit_swapper_g.html
  dcs_weather_editor_b.html

Sources images (à placer dans ./tiles/) :
  tiles/cp.webp  tiles/gu.webp  tiles/wx.webp
"""

import base64
import os
import sys

# ── Configuration ──────────────────────────────────────────────────────────────
APP_VERSION = '1.2.0'
OUT_FILE    = 'dist/dcs_mission_tools_final.html'

MODULES = [
    {'id': 'cp', 'src': 'dcs_comm_plan_editor_b.html',   'tile': 'tiles/cp.webp'},
    {'id': 'gu', 'src': 'dcs_ground_unit_swapper_g.html', 'tile': 'tiles/gu.webp'},
    {'id': 'wx', 'src': 'dcs_weather_editor_b.html',      'tile': 'tiles/wx.webp'},
]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def encode_file_b64(path):
    abs_path = os.path.join(SCRIPT_DIR, path)
    if not os.path.exists(abs_path):
        return None
    with open(abs_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('ascii')


def encode_module_b64(path):
    abs_path = os.path.join(SCRIPT_DIR, path)
    if not os.path.exists(abs_path):
        return None
    with open(abs_path, 'r', encoding='utf-8') as fh:
        html = fh.read()
    return base64.b64encode(html.encode('utf-8')).decode('ascii')


def build_module_html_js(modules):
    lines = ['const MODULE_HTML = {']
    for i, mod in enumerate(modules):
        b64 = encode_module_b64(mod['src'])
        if b64 is None:
            print(f'  [WARN] Source introuvable : {mod["src"]} — module {mod["id"]} désactivé', file=sys.stderr)
            b64 = ''
        comma = ',' if i < len(modules) - 1 else ''
        lines.append(f'  {mod["id"]}: "{b64}"{comma}')
        print(f'  [OK] Module {mod["id"]} — {len(b64)//1024} Ko base64 (UTF-8)')
    lines.append('};')
    return '\n'.join(lines)


def build_tile_uris(modules):
    uris = {}
    for mod in modules:
        b64 = encode_file_b64(mod['tile'])
        if b64 is None:
            print(f'  [WARN] Image tuile introuvable : {mod["tile"]} — placeholder utilisé', file=sys.stderr)
            uris[mod['id']] = ''
        else:
            uris[mod['id']] = f'data:image/webp;base64,{b64}'
            print(f'  [OK] Tuile {mod["id"]} — {len(b64)//1024} Ko base64')
    return uris


def build_html(module_html_js, tile_uris):

    tile_cp = tile_uris.get('cp', '')
    tile_gu = tile_uris.get('gu', '')
    tile_wx = tile_uris.get('wx', '')

    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DCS Mission Tools</title>
  <style>
    /* ── Palette Mission Suite (DESIGN_DCS_Mission_Suite.md §2) ── */
    :root {{
      --bg:           #1A1A1A;
      --surface:      #272727;
      --surface-2:    #2A2A2A;
      --surface-3:    #303030;
      --border:       #3C3C3C;
      --text:         #ECECEC;
      --text-2:       #CACACA;
      --text-dim:     #9E9E9E;

      --amber:        #FFB000;
      --amber-dim:    rgba(255,176,0,0.15);
      --amber-glow:   rgba(255,176,0,0.25);
      --olive:        #9CAE5A;
      --olive-dim:    rgba(156,174,90,0.15);
      --olive-glow:   rgba(156,174,90,0.25);
      --cyan:         #5AB8C9;
      --cyan-dim:     rgba(90,184,201,0.15);
      --cyan-glow:    rgba(90,184,201,0.25);

      --warn:         #FF8C00;
      --error:        #E53935;
      --success:      #4CAF50;

      --fam-armor:    #C9A66B;
      --fam-arti:     #B87C5A;
      --fam-sam:      #7D9CB8;
      --fam-radar:    #9C7DB8;
      --fam-aaa:      #B85A7D;
      --fam-logi:     #7DB89C;
      --fam-inf:      #B8B05A;
      --fam-infra:    #8A8A8A;
      --fam-unknown:  #5A5A5A;

      --font-ui:   system-ui, -apple-system, "Segoe UI", sans-serif;
      --font-mono: "Roboto Mono", "Courier New", monospace;

      /* Accent shell M·T */
      --mt-accent:     #7A9EBF;
      --mt-accent-dim: rgba(122,158,191,0.15);
      --mt-accent-glow:rgba(122,158,191,0.25);

      /* ── Hauteur wf-bar (compense le recouvrement fixed) ── */
      --wf-bar-h: 48px;
    }}

    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; height: 100%; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: var(--font-ui);
      font-size: 15px;
      line-height: 1.5;
      height: 100%;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}

    /* ── Header ── */
    #app-header {{
      background: var(--surface);
      border-bottom: 2px solid var(--mt-accent);
      padding: 10px 20px;
      display: flex;
      align-items: center;
      gap: 16px;
      position: sticky;
      top: 0;
      z-index: 100;
      flex-shrink: 0;
    }}
    .header-logo {{
      font-family: var(--font-mono);
      font-size: 15px;
      font-weight: 700;
      color: var(--mt-accent);
      letter-spacing: 0.05em;
    }}
    .header-title {{
      font-size: 14px;
      font-weight: 600;
      color: var(--text);
    }}
    .header-version {{
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--text-dim);
      background: var(--surface-2);
      padding: 2px 6px;
      border-radius: 3px;
    }}
    .header-right {{
      margin-left: auto;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    #btn-lang {{
      background: transparent;
      border: 1px solid var(--border);
      border-radius: 3px;
      padding: 3px 7px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 5px;
      font-family: var(--font-mono);
      font-size: 10px;
      color: var(--text-dim);
      transition: border-color 0.15s, color 0.15s;
    }}
    #btn-lang:hover {{
      border-color: var(--mt-accent);
      color: var(--mt-accent);
    }}
    #btn-lang svg {{ width: 18px; height: 12px; border-radius: 1px; display: block; }}

    /* En vue module : header shell masqué entièrement */
    #app-header.module-active {{ display: none; }}

    /* ── Shell main ── */
    #shell-main {{
      flex: 1;
      min-height: 0;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      position: relative;
    }}

    /* ══ LANDING ══ */
    #landing {{
      flex: 1;
      min-height: 0;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      padding: 40px 24px;
      /* Compenser le recouvrement de #wf-bar (fixed, hors flux) */
      padding-bottom: calc(40px + var(--wf-bar-h));
      gap: 0;
      position: relative;
      background:
        repeating-linear-gradient(
          -35deg,
          transparent,
          transparent 40px,
          rgba(255,255,255,0.012) 40px,
          rgba(255,255,255,0.012) 41px
        ),
        var(--bg);
    }}
    #landing::after {{
      content: '';
      position: fixed;
      inset: 0;
      background: radial-gradient(ellipse at center, transparent 60%, rgba(0,0,0,0.18));
      pointer-events: none;
      z-index: 0;
    }}
    #landing > * {{ position: relative; z-index: 1; }}

    /* Overlay drag-over */
    #landing.drag-over::before {{
      content: '';
      position: fixed;
      inset: 0;
      border: 3px dashed var(--mt-accent);
      background: rgba(122,158,191,0.07);
      z-index: 200;
      pointer-events: none;
    }}

    /* Wrapper centré */
    .landing-inner {{
      max-width: 1300px;
      margin: 0 auto;
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 28px;
    }}

    .landing-tagline {{
      text-align: center;
      color: #BFBFBF;
      font-family: var(--font-mono);
      font-size: 14px;
      letter-spacing: 0.15em;
      text-transform: uppercase;
    }}
    .section-title {{
      font-family: var(--font-mono);
      font-size: 13px;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      color: #CFCFCF;
      border-bottom: 1px solid #3C3C3C;
      padding-bottom: 6px;
      margin-bottom: 0;
    }}

    /* ── Grille cartes ── */
    #cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      justify-content: center;
      gap: 20px;
      perspective: 1500px;
    }}

    /* ── Carte module ── */
    .module-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 4px;
      padding: 0;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      position: relative;
      overflow: hidden;
      transform-style: preserve-3d;
      transform: rotateX(9deg) rotateY(-13deg);
      transition: transform .32s cubic-bezier(.2,.75,.2,1),
                  box-shadow .32s,
                  border-color .32s;
      outline: none;
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
    }}
    .module-card:focus-visible {{
      outline: 2px solid var(--mt-accent);
      outline-offset: 2px;
    }}
    .module-card:hover {{
      transform: rotateX(0) rotateY(0) translateY(-12px) scale(1.06);
      border-color: var(--card-accent);
      box-shadow: 0 18px 50px var(--card-glow);
      z-index: 5;
    }}

    /* Crochets HUD */
    .br {{
      position: absolute;
      width: 13px;
      height: 13px;
      border-color: var(--card-accent);
      opacity: .22;
      transition: opacity .32s;
      z-index: 2;
    }}
    .module-card:hover .br {{ opacity: 1; }}
    .br.tl  {{ top:7px;    left:7px;  border-top:2px solid; border-left:2px solid; }}
    .br.tr  {{ top:7px;    right:7px; border-top:2px solid; border-right:2px solid; }}
    .br.bl  {{ bottom:7px; left:7px;  border-bottom:2px solid; border-left:2px solid; }}
    .br.brr {{ bottom:7px; right:7px; border-bottom:2px solid; border-right:2px solid; }}

    /* Tuile image */
    .card-tile {{
      height: 148px;
      overflow: hidden;
      border-bottom: 1px solid var(--border);
      flex-shrink: 0;
      position: relative;
    }}
    .card-tile img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transition: transform .32s cubic-bezier(.2,.75,.2,1), filter .32s;
    }}
    .module-card:hover .card-tile img {{
      transform: scale(1.05);
      filter: brightness(1.08);
    }}
    .card-tile.no-img {{
      background: var(--surface-2);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: var(--font-mono);
      font-size: 28px;
      font-weight: 700;
      color: var(--card-accent, var(--text-dim));
      opacity: 0.4;
    }}

    /* Corps de carte */
    .card-body {{
      padding: 14px 16px 16px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .card-header-row {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .card-logo {{
      font-family: var(--font-mono);
      font-size: 14px;
      font-weight: 700;
      color: var(--card-accent, var(--text-dim));
      letter-spacing: 0.05em;
      flex-shrink: 0;
      background: var(--card-accent-dim, var(--surface-2));
      padding: 3px 6px;
      border-radius: 3px;
    }}
    .card-name {{
      font-size: 17px;
      font-weight: 600;
      color: #F2F2F2;
    }}
    .card-version {{
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--text-dim);
      background: #303030;
      padding: 1px 5px;
      border-radius: 2px;
      margin-left: auto;
      flex-shrink: 0;
    }}
    .card-descriptor {{
      font-size: 14px;
      color: var(--text-2);
      line-height: 1.5;
    }}
    .card-launch-hint {{
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--card-accent, var(--text-dim));
      letter-spacing: 0.1em;
      text-transform: uppercase;
      opacity: 0;
      transition: opacity .15s;
    }}
    .module-card:hover .card-launch-hint {{ opacity: 1; }}

    /* ── Cartes fantômes ── */
    .module-card.ghost {{
      opacity: 0.42;
      cursor: default;
      pointer-events: none;
      border-style: dashed;
      transform: rotateX(9deg) rotateY(-13deg);
    }}
    .ghost-badge {{
      position: absolute;
      top: 10px;
      right: 10px;
      font-family: var(--font-mono);
      font-size: 9px;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--text-dim);
      background: var(--surface-3);
      padding: 2px 6px;
      border-radius: 2px;
      border: 1px solid var(--border);
      z-index: 3;
    }}
    #ghost-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      justify-content: center;
      gap: 20px;
      perspective: 1500px;
    }}

    /* ══ VUE MODULE ══ */
    #module-view {{
      display: none;
      flex: 1;
      min-height: 0;
      position: relative;
    }}
    #module-view.active {{
      display: flex;
      flex-direction: column;
    }}
    #module-view iframe {{
      flex: 1;
      min-height: 0;
      width: 100%;
      border: none;
      display: block;
    }}
    #module-loading {{
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--bg);
      font-family: var(--font-mono);
      font-size: 12px;
      color: var(--text-dim);
      letter-spacing: 0.1em;
      pointer-events: none;
      z-index: 10;
    }}
    #module-loading.hidden {{ display: none; }}

    /* ══ BARRE FICHIER DE TRAVAIL ══
       Position fixed hors flux — zéro impact sur le layout landing/titre.
       Visible en landing uniquement (#wf-bar.in-module masqué). */
    #wf-bar {{
      position: fixed;
      left: 0; right: 0; bottom: 0;
      height: var(--wf-bar-h);
      z-index: 50;
      background: var(--surface);
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 0 20px;
    }}
    /* Masquer la wf-bar en vue module (le module gère sa propre barre de save) */
    #wf-bar.in-module {{ display: none; }}

    #wf-bar .wf-label {{
      font-family: var(--font-mono);
      font-size: 11px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--text-dim);
      flex-shrink: 0;
    }}
    #wf-bar .wf-filename {{
      font-family: var(--font-mono);
      font-size: 12px;
      color: var(--mt-accent);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      flex: 1;
      min-width: 0;
    }}
    #wf-bar .wf-filename.empty {{
      color: var(--text-dim);
      font-style: italic;
    }}
    #wf-bar .wf-btn {{
      background: transparent;
      border: 1px solid var(--border);
      border-radius: 3px;
      padding: 4px 12px;
      font-family: var(--font-mono);
      font-size: 11px;
      letter-spacing: 0.05em;
      color: var(--text-dim);
      cursor: pointer;
      flex-shrink: 0;
      transition: border-color 0.15s, color 0.15s;
      min-height: 30px;
    }}
    #wf-bar .wf-btn:hover {{
      border-color: var(--mt-accent);
      color: var(--mt-accent);
    }}
    #wf-bar .wf-btn.primary {{
      border-color: var(--mt-accent);
      color: var(--mt-accent);
    }}
    #wf-bar .wf-btn.primary:hover {{
      background: var(--mt-accent-dim);
    }}
    #wf-bar .wf-btn:disabled {{
      opacity: 0.35;
      cursor: default;
      pointer-events: none;
    }}

    /* ── Responsive ── */
    @media (max-width: 768px) {{
      #cards-grid, #ghost-grid {{
        grid-template-columns: 1fr;
        perspective: none;
      }}
      .module-card, .module-card.ghost {{ transform: none; }}
    }}
    @media (max-width: 600px) {{
      #landing {{ padding: 20px 14px calc(20px + var(--wf-bar-h)); }}
      .landing-inner {{ gap: 20px; }}
    }}
    @media (hover: none) {{
      .module-card:hover {{ transform: none; }}
    }}
    #btn-lang {{ min-height: 44px; min-width: 44px; }}
  </style>
</head>
<body>

  <!-- HEADER -->
  <header id="app-header">
    <div class="header-logo">M·T</div>
    <div class="header-title">DCS Mission Tools</div>
    <div class="header-version">v{APP_VERSION}</div>
    <div class="header-right">
      <button id="btn-lang" onclick="toggleLang()" title="Switch language / Changer de langue" aria-label="Changer la langue">
        <!-- drapeau injecté par JS -->
      </button>
    </div>
  </header>

  <!-- ZONE PRINCIPALE -->
  <div id="shell-main">

    <div id="landing">
      <div class="landing-inner">
        <div class="landing-tagline" data-i18n="tagline">DCS World · Mission Suite · v{APP_VERSION}</div>

        <div>
          <div class="section-title" data-i18n="sectionModules">Outils disponibles</div>
        </div>
        <div id="cards-grid"></div>

        <div>
          <div class="section-title" data-i18n="sectionRoadmap">Roadmap</div>
        </div>
        <div id="ghost-grid"></div>
      </div>
    </div>

    <div id="module-view">
      <div id="module-loading">CHARGEMENT…</div>
    </div>

  </div>

  <!-- BARRE FICHIER DE TRAVAIL (fixed, hors flux) -->
  <div id="wf-bar">
    <span class="wf-label" data-i18n="wf.label">Fichier de travail</span>
    <span class="wf-filename empty" id="wf-filename" data-i18n-empty="wf.none">Aucun fichier chargé</span>
    <button class="wf-btn primary" id="wf-btn-load" data-i18n="wf.load">Charger .miz</button>
    <button class="wf-btn" id="wf-btn-clear" disabled data-i18n="wf.clear">Vider</button>
    <input type="file" id="wf-file-input" accept=".miz" style="display:none">
  </div>

  <script>
    /* ═══════════════════════════════════════════
       DCS MISSION TOOLS — Shell v{APP_VERSION}
       Build : build_mission_tools.py
    ═══════════════════════════════════════════ */
    const APP_VERSION = '{APP_VERSION}';
    console.log('[M·T v' + APP_VERSION + '] Shell DCS Mission Tools — chargement');

    /* ── Modules embarqués en base64 (injectés par build) ── */
    {module_html_js}

    /* ── Décodage UTF-8 correct (correctif mojibake) ───────── */
    function decodeModule(b64) {{
      var bin = atob(b64);
      var bytes = new Uint8Array(bin.length);
      for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
      return new TextDecoder('utf-8').decode(bytes);
    }}

    /* ── i18n FR/EN ────────────────────────────────────────── */
    const I18N = {{
      fr: {{
        tagline:        'DCS World · Mission Suite · v{APP_VERSION}',
        sectionModules: 'Outils disponibles',
        sectionRoadmap: 'Roadmap',
        back:           'Mission Tools',
        loading:        'CHARGEMENT',
        soon:           'À venir',
        launch:         '► Ouvrir le module',
        'desc.cp': 'Éditeur de plan de communication — import/export .miz DCS.',
        'desc.gu': 'Remplacement de véhicules terrestres dans les missions .miz DCS.',
        'desc.wx': 'Édition des conditions météo dans les missions .miz DCS.',
        'desc.fc': "Configuration d\'un fichier config Foothold via template custom.",
        'desc.le': "Édition des loadouts et livrées d\'appareils (IA ou joueurs).",
        /* Fichier de travail */
        'wf.label': 'Fichier de travail',
        'wf.none':  'Aucun fichier chargé',
        'wf.load':  'Charger .miz',
        'wf.clear': 'Vider',
      }},
      en: {{
        tagline:        'DCS World · Mission Suite · v{APP_VERSION}',
        sectionModules: 'Available tools',
        sectionRoadmap: 'Roadmap',
        back:           'Mission Tools',
        loading:        'LOADING',
        soon:           'Soon',
        launch:         '► Open module',
        'desc.cp': 'Communication plan editor — .miz import/export for DCS.',
        'desc.gu': 'Ground vehicle replacement in DCS .miz missions.',
        'desc.wx': 'Weather conditions editor for DCS .miz missions.',
        'desc.fc': 'Foothold config file setup via a custom template.',
        'desc.le': 'Edit aircraft loadouts and liveries (AI or player).',
        /* Working file */
        'wf.label': 'Working file',
        'wf.none':  'No file loaded',
        'wf.load':  'Load .miz',
        'wf.clear': 'Clear',
      }}
    }};

    const KEY_LANG = 'lang_v1';
    let CURRENT_LANG = 'fr';

    function t(key) {{
      const d = I18N[CURRENT_LANG] || I18N.fr;
      if (key in d) return d[key];
      if (key in I18N.fr) return I18N.fr[key];
      return key;
    }}

    function initLang() {{
      try {{
        const stored = localStorage.getItem(KEY_LANG);
        if (stored === 'fr' || stored === 'en') {{ CURRENT_LANG = stored; return; }}
      }} catch(e) {{}}
      const nav = (navigator.language || 'fr').toLowerCase();
      CURRENT_LANG = nav.startsWith('fr') ? 'fr' : 'en';
    }}

    const FLAG_FR = '<svg viewBox="0 0 18 12" xmlns="http://www.w3.org/2000/svg"><rect width="6" height="12" fill="#002395"/><rect x="6" width="6" height="12" fill="#fff"/><rect x="12" width="6" height="12" fill="#ED2939"/></svg>';
    const FLAG_GB = '<svg viewBox="0 0 18 12" xmlns="http://www.w3.org/2000/svg"><rect width="18" height="12" fill="#012169"/><path d="M0,0 L18,12 M18,0 L0,12" stroke="#fff" stroke-width="2.4"/><path d="M0,0 L18,12 M18,0 L0,12" stroke="#C8102E" stroke-width="1.2"/><path d="M9,0 V12 M0,6 H18" stroke="#fff" stroke-width="3"/><path d="M9,0 V12 M0,6 H18" stroke="#C8102E" stroke-width="1.8"/></svg>';

    function updateFlagButton() {{
      const btn = document.getElementById('btn-lang');
      if (!btn) return;
      if (CURRENT_LANG === 'fr') {{
        btn.innerHTML = FLAG_GB;
        btn.title = 'Switch to English';
      }} else {{
        btn.innerHTML = FLAG_FR;
        btn.title = 'Passer en français';
      }}
    }}

    function applyI18nStatic() {{
      document.querySelectorAll('[data-i18n]').forEach(function(el) {{
        const key = el.getAttribute('data-i18n');
        const val = t(key);
        if (val !== key) el.textContent = val;
      }});
      document.documentElement.lang = CURRENT_LANG;
      /* wf-filename : texte "aucun" si pas de fichier */
      updateWfBar();
    }}

    function setLang(lang) {{
      CURRENT_LANG = lang;
      try {{ localStorage.setItem(KEY_LANG, lang); }} catch(e) {{}}
      applyI18nStatic();
      updateFlagButton();
      renderCards();
      renderGhosts();
    }}

    function toggleLang() {{
      setLang(CURRENT_LANG === 'fr' ? 'en' : 'fr');
    }}

    /* ── Manifest modules ─────────────────────────────────── */
    const MODULES = [
      {{
        id:         'cp',
        logo:       'C·P',
        name:       'Comm Plan Editor',
        version:    'v1.1.0',
        accent:     '#FFB000',
        accentDim:  'rgba(255,176,0,0.15)',
        accentGlow: 'rgba(255,176,0,0.25)',
        descKey:    'desc.cp',
        tile:       '{tile_cp}',
      }},
      {{
        id:         'gu',
        logo:       'G·U',
        name:       'Ground Unit Swapper',
        version:    'v1.3.1',
        accent:     '#9CAE5A',
        accentDim:  'rgba(156,174,90,0.15)',
        accentGlow: 'rgba(156,174,90,0.25)',
        descKey:    'desc.gu',
        tile:       '{tile_gu}',
      }},
      {{
        id:         'wx',
        logo:       'W·X',
        name:       'Weather Editor',
        version:    'v1.1.0',
        accent:     '#5AB8C9',
        accentDim:  'rgba(90,184,201,0.15)',
        accentGlow: 'rgba(90,184,201,0.25)',
        descKey:    'desc.wx',
        tile:       '{tile_wx}',
      }},
    ];

    const COMING_SOON = [
      {{ id:'fc', logo:'F·C', name:'Foothold Configurator', descKey:'desc.fc' }},
      {{ id:'le', logo:'L·E', name:'Loadout Editor',        descKey:'desc.le' }},
    ];

    /* ── State ───────────────────────────────────────────── */
    const iframes = {{}};
    let activeModule = null;

    /* ══ FICHIER DE TRAVAIL — state ══
       workingFile : File | null
       Le File est recrée depuis des ArrayBuffer à l\'injection cross-realm (Phase B).
       injectedFilePerModule : {{id: filename}} — évite les injections dupliquées. */
    let workingFile = null;
    const injectedFilePerModule = {{}};

    /* ── Callback de sauvegarde exposé aux modules ── */
    window.MT_onModuleSave = function(blob, filename) {{
      /* Met à jour workingFile avec le .miz sauvé par le module.
         Le File sera reconstruit au bon realm à la prochaine injection. */
      try {{
        workingFile = new File([blob], filename, {{ type: 'application/octet-stream' }});
        /* Invalider le cache d'injection pour tous les modules :
           le fichier a changé, il faudra ré-injecter partout. */
        Object.keys(injectedFilePerModule).forEach(function(id) {{
          injectedFilePerModule[id] = null;
        }});
        updateWfBar();
        console.log('[M·T] MT_onModuleSave — fichier de travail mis à jour :', filename);
      }} catch(e) {{
        console.warn('[M·T] MT_onModuleSave — erreur :', e);
      }}
    }};

    /* ── Injection cross-realm du fichier de travail dans un module ── */
    async function injectWorkingFile(iframe, id) {{
      if (!workingFile) return;
      if (injectedFilePerModule[id] === workingFile.name) return;
      var win = iframe.contentWindow;
      var doc = iframe.contentDocument;
      if (!win || !doc) return;
      var input = doc.getElementById('file-input');
      if (!input) return;
      try {{
        var bytes = new Uint8Array(await workingFile.arrayBuffer());
        var childFile = new win.File([bytes], workingFile.name, {{ type: 'application/octet-stream' }});
        var dt = new win.DataTransfer();
        dt.items.add(childFile);
        input.files = dt.files;
        input.dispatchEvent(new win.Event('change', {{ bubbles: true }}));
        injectedFilePerModule[id] = workingFile.name;
        console.log('[M·T] Fichier injecté dans module', id, ':', workingFile.name);
      }} catch(e) {{
        console.error('[M·T] injectWorkingFile — erreur cross-realm :', e);
      }}
    }}

    function updateWfBar() {{
      const fnEl  = document.getElementById('wf-filename');
      const btnCl = document.getElementById('wf-btn-clear');
      if (!fnEl) return;
      if (workingFile) {{
        fnEl.textContent = workingFile.name;
        fnEl.classList.remove('empty');
        if (btnCl) btnCl.disabled = false;
      }} else {{
        fnEl.textContent = t('wf.none');
        fnEl.classList.add('empty');
        if (btnCl) btnCl.disabled = true;
      }}
    }}

    function setWorkingFile(file) {{
      workingFile = file || null;
      updateWfBar();
      console.log('[M·T] Fichier de travail :', workingFile ? workingFile.name : '(vide)');
    }}

    function clearWorkingFile() {{
      setWorkingFile(null);
    }}

    /* ── Handlers boutons wf-bar ── */
    document.addEventListener('DOMContentLoaded', function() {{
      document.getElementById('wf-btn-load').addEventListener('click', function() {{
        document.getElementById('wf-file-input').click();
      }});
      document.getElementById('wf-btn-clear').addEventListener('click', clearWorkingFile);
      document.getElementById('wf-file-input').addEventListener('change', function(e) {{
        var f = e.target.files && e.target.files[0];
        if (f) setWorkingFile(f);
        /* reset input pour permettre re-sélection du même fichier */
        e.target.value = '';
      }});
    }});

    /* ── Drag & drop .miz sur #landing ── */
    document.addEventListener('DOMContentLoaded', function() {{
      var landing = document.getElementById('landing');

      landing.addEventListener('dragover', function(e) {{
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
        landing.classList.add('drag-over');
      }});
      landing.addEventListener('dragleave', function(e) {{
        /* Ne retirer le class que si on quitte vraiment #landing */
        if (!landing.contains(e.relatedTarget)) {{
          landing.classList.remove('drag-over');
        }}
      }});
      landing.addEventListener('drop', function(e) {{
        e.preventDefault();
        landing.classList.remove('drag-over');
        var files = e.dataTransfer.files;
        for (var i = 0; i < files.length; i++) {{
          if (files[i].name.endsWith('.miz')) {{
            setWorkingFile(files[i]);
            break;
          }}
        }}
      }});
    }});

    /* ── Rendu cartes ────────────────────────────────────── */
    function renderCards() {{
      const grid = document.getElementById('cards-grid');
      grid.innerHTML = '';

      MODULES.forEach(function(mod) {{
        const card = document.createElement('div');
        card.className = 'module-card';
        card.tabIndex = 0;
        card.setAttribute('role', 'button');
        card.setAttribute('aria-label', mod.name);

        card.style.setProperty('--card-accent',     mod.accent);
        card.style.setProperty('--card-accent-dim', mod.accentDim);
        card.style.setProperty('--card-glow',       mod.accentGlow);

        const tileHtml = mod.tile
          ? '<div class="card-tile"><img src="' + mod.tile + '" alt="" loading="lazy"></div>'
          : '<div class="card-tile no-img">' + mod.logo + '</div>';

        card.innerHTML =
          '<span class="br tl"></span><span class="br tr"></span>' +
          '<span class="br bl"></span><span class="br brr"></span>' +
          tileHtml +
          '<div class="card-body">' +
            '<div class="card-header-row">' +
              '<div class="card-logo">' + mod.logo + '</div>' +
              '<div class="card-name">' + mod.name + '</div>' +
              '<div class="card-version">' + mod.version + '</div>' +
            '</div>' +
            '<div class="card-descriptor">' + t(mod.descKey) + '</div>' +
            '<div class="card-launch-hint">' + t('launch') + '</div>' +
          '</div>';

        card.addEventListener('click', function() {{ openModule(mod.id); }});
        card.addEventListener('keydown', function(e) {{
          if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); openModule(mod.id); }}
        }});

        grid.appendChild(card);
      }});
    }}

    function renderGhosts() {{
      const grid = document.getElementById('ghost-grid');
      grid.innerHTML = '';

      COMING_SOON.forEach(function(cs) {{
        const card = document.createElement('div');
        card.className = 'module-card ghost';
        card.setAttribute('aria-hidden', 'true');
        card.innerHTML =
          '<div class="ghost-badge">' + t('soon') + '</div>' +
          '<div class="card-tile no-img" style="font-size:22px;opacity:0.2">' + cs.logo + '</div>' +
          '<div class="card-body">' +
            '<div class="card-header-row">' +
              '<div class="card-logo" style="color:var(--text-dim);background:var(--surface-3)">' + cs.logo + '</div>' +
              '<div class="card-name">' + cs.name + '</div>' +
            '</div>' +
            '<div class="card-descriptor">' + t(cs.descKey) + '</div>' +
          '</div>';
        grid.appendChild(card);
      }});
    }}

    /* ── Garde édits non sauvegardés ────────────────────── */
    function hasUnsavedEdits(id) {{
      if (!iframes[id]) return false;
      try {{
        var win = iframes[id].contentWindow;
        if (!win || !win.UI_STATE) return false;
        var edits = win.UI_STATE.edits;
        if (!edits) return false;
        /* CP et GU : Map → .size ; WX : objet plain → Object.keys */
        if (typeof edits.size === 'number') return edits.size > 0;
        return Object.keys(edits).length > 0;
      }} catch(e) {{
        return false;
      }}
    }}

    /* ── Navigation ──────────────────────────────────────── */
    function openModule(id) {{
      const mod = MODULES.find(function(m) {{ return m.id === id; }});
      if (!mod) return;
      if (!MODULE_HTML[id]) {{
        console.warn('[M·T] Module ' + id + ' : base64 vide, abandon');
        return;
      }}

      document.getElementById('landing').style.display = 'none';
      const moduleView = document.getElementById('module-view');
      moduleView.classList.add('active');

      document.getElementById('app-header').classList.add('module-active');
      /* Masquer wf-bar en vue module */
      document.getElementById('wf-bar').classList.add('in-module');

      Object.keys(iframes).forEach(function(iid) {{ iframes[iid].style.display = 'none'; }});

      if (!iframes[id]) {{
        const loading = document.getElementById('module-loading');
        loading.classList.remove('hidden');
        loading.textContent = t('loading') + ' ' + mod.name.toUpperCase() + '…';

        const iframe = document.createElement('iframe');
        iframe.id = 'iframe-' + id;
        iframe.title = mod.name;
        iframe.srcdoc = decodeModule(MODULE_HTML[id]);

        iframe.addEventListener('load', function() {{
          loading.classList.add('hidden');
          var doc = iframe.contentDocument;
          var hdr = doc && doc.getElementById('app-header');
          if (hdr && !hdr.querySelector('.mt-back-injected')) {{
            var back = doc.createElement('button');
            back.className = 'mt-back-injected';
            back.textContent = '◄ Mission Tools';
            back.style.cssText = 'font-family:inherit;font-size:11px;cursor:pointer;color:#7A9EBF;'
              + 'background:transparent;border:1px solid #7A9EBF;border-radius:3px;padding:4px 10px;'
              + 'margin-right:12px;letter-spacing:.03em;min-height:36px;flex-shrink:0;';
            back.addEventListener('click', goHub);
            hdr.insertBefore(back, hdr.firstChild);
            var lang = hdr.querySelector('#btn-lang');
            if (lang) hdr.appendChild(lang);
          }}
          /* ── Injection fichier de travail (cross-realm) ── */
          injectWorkingFile(iframe, id);
          console.log('[M·T v' + APP_VERSION + '] Module ' + id + ' chargé');
        }});

        moduleView.appendChild(iframe);
        iframes[id] = iframe;
      }} else {{
        iframes[id].style.display = 'block';
        document.getElementById('module-loading').classList.add('hidden');
        injectWorkingFile(iframes[id], id);
      }}

      activeModule = id;
    }}

    function goHub() {{
      /* Garde : édits non sauvegardées dans le module actif */
      if (activeModule && hasUnsavedEdits(activeModule)) {{
        var modName = (MODULES.find(function(m) {{ return m.id === activeModule; }}) || {{}}).name || activeModule;
        var msg = CURRENT_LANG === 'fr'
          ? modName + ' : des modifications ne sont pas sauvegardées. Quitter quand même ?'
          : modName + ': unsaved changes. Leave anyway?';
        if (!window.confirm(msg)) return;
      }}
      Object.keys(iframes).forEach(function(iid) {{ iframes[iid].style.display = 'none'; }});
      document.getElementById('module-view').classList.remove('active');
      document.getElementById('landing').style.display = 'flex';
      document.getElementById('app-header').classList.remove('module-active');
      /* Réafficher wf-bar au retour landing */
      document.getElementById('wf-bar').classList.remove('in-module');
      activeModule = null;
      try {{
        var storedLang = localStorage.getItem(KEY_LANG);
        if (storedLang && storedLang !== CURRENT_LANG && (storedLang === 'fr' || storedLang === 'en')) {{
          CURRENT_LANG = storedLang;
          applyI18nStatic();
          updateFlagButton();
          renderCards();
          renderGhosts();
        }}
      }} catch(e) {{}}
    }}

    /* ── Init ────────────────────────────────────────────── */
    function init() {{
      initLang();
      applyI18nStatic();
      updateFlagButton();
      renderCards();
      renderGhosts();
      console.log('[M·T v' + APP_VERSION + '] Initialisé — ' + MODULES.length + ' modules, langue: ' + CURRENT_LANG);
    }}

    document.addEventListener('DOMContentLoaded', init);
  </script>
</body>
</html>'''


def main():
    print(f'=== build_mission_tools.py — DCS Mission Tools v{APP_VERSION} ===')

    os.makedirs(os.path.join(SCRIPT_DIR, 'dist'), exist_ok=True)

    print('\n[1/3] Encodage modules HTML…')
    module_html_js = build_module_html_js(MODULES)

    print('\n[2/3] Encodage images tuiles…')
    tile_uris = build_tile_uris(MODULES)

    print(f'\n[3/3] Génération {OUT_FILE}…')
    html = build_html(module_html_js, tile_uris)

    out_path = os.path.join(SCRIPT_DIR, OUT_FILE)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    size_kb = os.path.getsize(out_path) // 1024
    print(f'\n✓ Fichier généré : {out_path}')
    print(f'  Taille : {size_kb} Ko')
    print('\n=== Build terminé ===')


if __name__ == '__main__':
    main()
