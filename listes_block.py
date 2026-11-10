#!/usr/bin/env python3
"""Bloc « LISTES DÉROULANTES AU THÈME » — une seule source pour les quatre outils de Mission Tools.

Rend le texte JavaScript du bloc : le composant des listes de Mission Plan (dcs-mission-plan, build_datacard_generator.py,
« LISTES DE LA BARRE », MIT), repris avec les seuls écarts suivants :
  - un seul point d'entrée, initListes({ label, search }) : le bloc ne dépend d'aucune fonction de la page, les textes
    (intitulé de la liste, champ de recherche, « aucun résultat ») lui sont passés à l'initialisation ;
  - le CSS est dans le bloc (chaîne injectée en tête du <head> : les règles de l'outil, à égalité, passent après) ;
  - l'accent est la variable --tbm-accent, que chaque outil pose dans son :root ;
  - un champ de recherche en tête de toute liste de plus de 15 choix ;
  - un seul observateur des mutations pour toute la page (celui de la page, qui suit aussi les options, le libellé et
    les classes de chaque <select>), au lieu d'un par <select> ;
  - les classes du <select> sont recopiées sur son bouton à chaque changement ;
  - un <select> marqué data-tbm-skip n'est jamais rattaché ;
  - plus de mode « barre » ni de dépendance à header.toolbar / .tab-bar ni de ResizeObserver par bouton.
Le bloc est identique à l'octet dans les quatre modules : build_mission_tools.py le garde (build en code 1 sinon).

Usage (par le build) : from listes_block import build_block ; texte = build_block()
"""

BLOCK_BEGIN = '/* ===== LISTES DEROULANTES AU THEME ===== */'
BLOCK_END = '/* ===== FIN DES LISTES DEROULANTES ===== */'

_JS = r"""
/* Le <select> reste dans la page (id, options, écouteurs, valeur) mais masqué ; un <button> le remplace et porte le
   libellé ; la liste ouverte est un <ul role="listbox"> posé en fin de <body>. initListes() rattache tout <select>
   présent ou inséré ensuite. Au-delà de 15 choix, un champ de recherche reste en tête de la liste.
   Réglages de l'outil : variable --tbm-accent dans :root ; initListes({ label: select => intitulé,
   search: () => [texte du champ, texte « aucun résultat »] }). */
const TBM_CSS = `
select[data-tbm-src] { display: none !important; }
.tbm-trigger { display: inline-block; position: relative; box-sizing: border-box; min-width: 120px; min-height: 26px; margin: 0; padding: 3px 24px 3px 8px; background: var(--surface-2); border: 1px solid var(--border); border-radius: 4px; color: var(--text); font: inherit; font-size: 11px; text-align: left; white-space: nowrap; cursor: pointer; }
.tbm-trigger::after { content: '▾'; position: absolute; right: 8px; top: 50%; transform: translateY(-50%); color: var(--text-dim); font-size: 10px; line-height: 1; }
.tbm-trigger:hover, .tbm-trigger:focus-visible { border-color: var(--tbm-accent); outline: none; }
.tbm-trigger-open { border-color: var(--tbm-accent) !important; }
.tbm-trigger:disabled { opacity: .5; cursor: not-allowed; }
.tbm-lbl { display: block; min-width: 0; margin-right: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; text-align: left; pointer-events: none; }
.tbm-lbl::after { content: attr(data-w); display: block; height: 0; overflow: hidden; visibility: hidden; white-space: pre; }
@supports (width: calc-size(max-content, round(up, size, 1px))) { .tbm-lbl::after { width: calc-size(max-content, round(up, size, 1px)); } }
.tbm-panel {
  position: fixed; z-index: 10500; box-sizing: border-box; min-width: 180px; max-width: min(520px, calc(100vw - 16px));
  max-height: min(62vh, 440px); overflow-y: auto; overscroll-behavior: contain;
  background: var(--surface); border: 1px solid var(--tbm-accent); border-top: 3px solid var(--tbm-accent);
  box-shadow: 0 12px 28px rgba(0,0,0,.55), 0 2px 0 rgba(0,0,0,.35);
  padding: 4px 0; margin: 0; list-style: none; scrollbar-width: thin; scrollbar-color: var(--tbm-accent) transparent;
  transform-origin: top left; animation: tbm-in .12s ease-out;
}
.tbm-panel, .tbm-panel:focus, .tbm-panel:focus-visible { outline: none; }
.tbm-panel.tbm-up { border-top: 1px solid var(--tbm-accent); border-bottom: 3px solid var(--tbm-accent); transform-origin: bottom left; }
@keyframes tbm-in { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: none; } }
.tbm-head {
  font-family: var(--font-ui); font-weight: 500; font-size: 10px; letter-spacing: 1.2px; text-transform: uppercase;
  color: var(--text-2); padding: 8px 14px 6px; border-bottom: 1px solid var(--border); margin-bottom: 2px;
}
.tbm-search { position: sticky; top: 0; z-index: 2; background: var(--surface); padding: 6px 10px 8px; border-bottom: 1px solid var(--border); list-style: none; }
.tbm-search input { display: block; box-sizing: border-box; width: 100%; background: var(--surface-2); border: 1px solid var(--border); color: var(--text); font: 13px var(--font-ui); padding: 6px 8px; border-radius: 4px; margin: 0; }
.tbm-search input:focus { outline: none; border-color: var(--tbm-accent); }
.tbm-opt {
  position: relative; display: flex; align-items: center; gap: 10px; min-height: 36px; padding: 0 16px 0 18px;
  font-family: var(--font-ui); font-weight: 500; font-size: 12px; letter-spacing: 0; text-transform: none;
  color: var(--text); cursor: pointer; white-space: nowrap; user-select: none;
}
.tbm-opt .tbm-txt { min-width: 0; overflow: hidden; text-overflow: ellipsis; }
.tbm-opt + .tbm-opt { border-top: 1px solid var(--border); }
.tbm-opt .tbm-mark { width: 7px; height: 7px; flex: none; transform: rotate(45deg); border: 1px solid var(--text-dim); box-sizing: border-box; }
.tbm-opt.active, .tbm-opt:hover { background: var(--surface-2); background: color-mix(in srgb, var(--tbm-accent) 15%, transparent); color: var(--tbm-accent); }
.tbm-opt.active .tbm-mark, .tbm-opt:hover .tbm-mark { border-color: var(--tbm-accent); }
.tbm-opt[aria-selected="true"] { color: var(--tbm-accent); font-weight: 700; }
.tbm-opt[aria-selected="true"]::before { content: ''; position: absolute; left: 0; top: 6px; bottom: 6px; width: 3px; background: var(--tbm-accent); }
.tbm-opt[aria-selected="true"] .tbm-mark { background: var(--tbm-accent); border-color: var(--tbm-accent); }
.tbm-opt[aria-disabled="true"] { color: var(--text-dim); cursor: not-allowed; background: none; }
.tbm-opt[aria-disabled="true"] .tbm-mark { border-style: dashed; border-color: var(--text-dim); background: none; }
.tbm-opt[aria-disabled="true"] .tbm-note { color: var(--text-dim); font-size: 10px; letter-spacing: 1px; margin-left: auto; padding-left: 14px; }
.tbm-opt.tbm-hide { display: none; }
.tbm-group {
  font-family: var(--font-ui); font-weight: 500; font-size: 10px; letter-spacing: 1.2px; text-transform: uppercase;
  color: var(--text-2); padding: 10px 14px 4px; list-style: none; cursor: default; user-select: none; border-top: 1px solid var(--border);
}
.tbm-group:first-child, .tbm-head + .tbm-group, .tbm-search + .tbm-group { border-top: 0; }
.tbm-group.tbm-hide { display: none; }
.tbm-none { padding: 10px 14px; color: var(--text-dim); font-family: var(--font-ui); font-size: 12px; text-align: center; list-style: none; }
.tbm-none.tbm-hide { display: none; }
@media (pointer: coarse) { .tbm-opt { min-height: 44px; } .tbm-search input { font-size: 16px; } }
@media (prefers-reduced-motion: reduce) { .tbm-panel { animation: none; } }
@media print { .tbm-panel { display: none; } }
`;

const TBM = { cur: null, bound: false, swallow: false, styled: false, n: 0, all: [], map: new WeakMap(), label: null, texts: null, mo: null };

function initListes(cfg) {
  TBM.label = cfg.label;
  TBM.texts = cfg.search;
  if (!TBM.styled) {
    TBM.styled = true;
    const st = document.createElement('style');
    st.id = 'tbm-style';
    st.textContent = TBM_CSS;
    document.head.insertBefore(st, document.head.firstChild);
  }
  if (!TBM.bound) {
    TBM.bound = true;
    document.addEventListener('pointerdown', tbmOutside, true);
    window.addEventListener('click', tbmSwallowClick, true);
    window.addEventListener('resize', tbmResized);
    window.addEventListener('blur', () => tbmClose(false));
    window.addEventListener('scroll', tbmScrolled, true);
    if (window.visualViewport) window.visualViewport.addEventListener('resize', tbmViewport);
  }
  tbmScan(document.body);
  if (TBM.mo) return;
  TBM.mo = new MutationObserver(tbmMutations);
  TBM.mo.observe(document.body, {
    childList: true, subtree: true, characterData: true, attributes: true,
    attributeFilter: ['title', 'aria-label', 'disabled', 'label', 'selected', 'value', 'class']
  });
}

/* Un seul observateur pour la page : un <select> inséré est rattaché ; un <select> sorti de la page est détaché
   (la liste ouverte sur lui se ferme) ; une option, un libellé ou une classe qui change remet son bouton à jour. */
function tbmMutations(recs) {
  const dirty = new Set();
  let gone = false;
  for (let i = 0; i < recs.length; i++) {
    const r = recs[i];
    if (r.type === 'childList') {
      for (let j = 0; j < r.addedNodes.length; j++) if (r.addedNodes[j].nodeType === 1) tbmScan(r.addedNodes[j]);
      if (r.removedNodes.length) gone = true;
      tbmMark(dirty, r.target);
    } else if (r.type === 'attributes') tbmMark(dirty, r.target);
    else tbmMark(dirty, r.target.parentNode);
  }
  if (gone) {
    const keep = [];
    for (let i = 0; i < TBM.all.length; i++) {
      const m = TBM.all[i];
      if (m.sel.isConnected) keep.push(m); else tbmForget(m);
    }
    TBM.all = keep;
  }
  dirty.forEach(m => { if (m.sel.isConnected) tbmSync(m); });
}

function tbmMark(set, node) {
  if (!node || node.nodeType !== 1) return;
  const tag = node.tagName;
  const s = tag === 'SELECT' ? node : (tag === 'OPTION' || tag === 'OPTGROUP' ? node.closest('select') : null);
  const m = s ? TBM.map.get(s) : null;
  if (m) set.add(m);
}

function tbmScan(root) {
  if (!TBM.label || !root || root.nodeType !== 1 || root.classList.contains('tbm-panel')) return;
  if (root.tagName !== 'SELECT' && !root.firstElementChild) return;
  const list = root.tagName === 'SELECT' ? [root] : Array.prototype.slice.call(root.querySelectorAll('select'));
  list.forEach(tbmAttach);
}

function tbmForget(m) {
  if (TBM.cur === m) tbmClose(false);
  if (m.btn.parentNode) m.btn.parentNode.removeChild(m.btn);
  TBM.map.delete(m.sel);
}

function tbmAttach(sel) {
  if (!sel || !sel.parentNode || TBM.map.has(sel) || sel.hasAttribute('data-tbm-skip')) return;
  const uid = sel.id || 'f' + (++TBM.n);
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'tbm-trigger';
  btn.setAttribute('aria-haspopup', 'listbox');
  btn.setAttribute('aria-expanded', 'false');
  btn.setAttribute('aria-controls', 'tbm-list-' + uid);
  const lbl = document.createElement('span');
  lbl.className = 'tbm-lbl';
  btn.appendChild(lbl);
  const m = {
    sel: sel, btn: btn, lbl: lbl, panel: null, active: -1, actLi: null, type: '', typeTimer: 0,
    x0: 0, y0: 0, w0: 0, uid: uid, cls: '', lis: [], norm: [], search: null, searchBox: null, none: null
  };
  sel.parentNode.insertBefore(btn, sel);
  sel.setAttribute('data-tbm-src', '');
  ['value', 'selectedIndex'].forEach(k => {
    const d = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, k);
    if (!d || !d.set) return;
    Object.defineProperty(sel, k, {
      configurable: true, enumerable: true,
      get() { return d.get.call(this); },
      set(v) { d.set.call(this, v); tbmSync(m); }
    });
  });
  TBM.map.set(sel, m);
  TBM.all.push(m);
  sel.addEventListener('change', () => tbmSync(m));
  ['focus', 'mouseover'].forEach(ev => btn.addEventListener(ev, () => tbmSync(m)));   /* filet : option.selected posé par le code */
  btn.addEventListener('click', () => { if (m.panel) tbmClose(true); else tbmOpen(m); });
  btn.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      if (!m.panel) tbmOpen(m);
    }
  });
  tbmSync(m);
}

function tbmName(m) {
  let name = '';
  try { name = TBM.label(m.sel) || ''; } catch (e) { name = ''; }
  return name;
}

/* Le libellé affiché = l'option choisie ; la largeur = l'option la plus large (comme le <select>), jusqu'à 200 choix ;
   les classes du <select> suivent sur le bouton */
function tbmSync(m) {
  const sel = m.sel, o = sel.options, i = sel.selectedIndex;
  const cls = sel.className;
  if (cls !== m.cls) {
    m.cls.split(/\s+/).forEach(c => { if (c) m.btn.classList.remove(c); });
    cls.split(/\s+/).forEach(c => { if (c) m.btn.classList.add(c); });
    m.cls = cls;
  }
  const txt = i >= 0 && o[i] ? o[i].label : '';
  if (m.lbl.textContent !== txt) m.lbl.textContent = txt;
  let w = '';
  if (o.length <= 200) {
    const all = [];
    for (let k = 0; k < o.length; k++) all.push(o[k].label);
    w = all.join(String.fromCharCode(10));
  }
  if ((m.lbl.getAttribute('data-w') || '') !== w) m.lbl.setAttribute('data-w', w);
  const name = tbmName(m);
  if (m.btn.getAttribute('aria-label') !== name) m.btn.setAttribute('aria-label', name);
  if (sel.hasAttribute('title')) { if (m.btn.title !== sel.title) m.btn.title = sel.title; } else if (m.btn.hasAttribute('title')) m.btn.removeAttribute('title');
  if (m.btn.disabled !== sel.disabled) m.btn.disabled = sel.disabled;
}

/* Sans casse ni accents */
function tbmNorm(s) {
  return String(s).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
}

function tbmTexts() {
  let t = null;
  try { t = TBM.texts(); } catch (e) { t = null; }
  return [t && t[0] ? t[0] : 'Rechercher…', t && t[1] ? t[1] : 'Aucun résultat'];
}

function tbmOpen(m) {
  if (TBM.cur) tbmClose(false);
  if (m.sel.disabled) return;
  tbmSync(m);
  const sel = m.sel, opts = sel.options, name = tbmName(m);
  const ul = document.createElement('ul');
  ul.className = 'tbm-panel';
  ul.id = 'tbm-list-' + m.uid;
  ul.setAttribute('role', 'listbox');
  if (name) ul.setAttribute('aria-label', name);
  ul.tabIndex = -1;
  if (name) {   /* jamais d'en-tête vide : sans intitulé, pas d'en-tête */
    const head = document.createElement('li');
    head.className = 'tbm-head';
    head.setAttribute('role', 'presentation');
    head.textContent = name;
    ul.appendChild(head);
  }
  const tx = tbmTexts();
  m.search = null;
  if (opts.length > 15) {
    const sl = document.createElement('li');
    sl.className = 'tbm-search';
    sl.setAttribute('role', 'presentation');
    const inp = document.createElement('input');
    inp.type = 'text';
    inp.placeholder = tx[0];
    inp.setAttribute('aria-label', tx[0]);
    inp.setAttribute('autocomplete', 'off');
    inp.setAttribute('autocapitalize', 'off');
    inp.setAttribute('spellcheck', 'false');
    sl.appendChild(inp);
    ul.appendChild(sl);
    inp.addEventListener('input', () => tbmFilter(m, inp.value));
    m.search = inp;
    m.searchBox = sl;
  }
  m.lis = [];
  m.norm = [];
  m.grps = [];   /* les titres de groupes : { li, first, last } (index des options du groupe) ; un titre n'est pas une option */
  let grp = null, grpNode = null;
  const frag = document.createDocumentFragment();
  for (let k = 0; k < opts.length; k++) {
    const o = opts[k], li = document.createElement('li');
    const og = o.parentNode && o.parentNode.tagName === 'OPTGROUP' ? o.parentNode : null;
    if (og !== grpNode) {
      grpNode = og;
      grp = null;
      if (og && og.label) {   /* un label vide ou absent : pas de titre */
        const gl = document.createElement('li');
        gl.className = 'tbm-group';
        gl.setAttribute('role', 'presentation');
        gl.textContent = og.label;
        frag.appendChild(gl);
        grp = { li: gl, first: k, last: k };
        m.grps.push(grp);
      }
    }
    if (grp) grp.last = k;
    li.className = 'tbm-opt';
    li.id = 'tbm-' + m.uid + '-' + k;
    li.setAttribute('role', 'option');
    li.setAttribute('aria-selected', k === sel.selectedIndex ? 'true' : 'false');
    li.setAttribute('data-i', String(k));
    const mark = document.createElement('span');
    mark.className = 'tbm-mark';
    const txt = document.createElement('span');
    txt.className = 'tbm-txt';
    let label = o.label, note = '';
    if (o.disabled) {
      li.setAttribute('aria-disabled', 'true');
      const j = label.indexOf(' — ');
      if (j >= 0) { note = label.slice(j + 3); label = label.slice(0, j); }
    }
    txt.textContent = label;
    li.appendChild(mark);
    li.appendChild(txt);
    if (note) {
      const n = document.createElement('span');
      n.className = 'tbm-note';
      n.textContent = note;
      li.appendChild(n);
    }
    m.lis.push(li);
    if (m.search) m.norm.push(tbmNorm(o.label));
    frag.appendChild(li);
  }
  ul.appendChild(frag);
  const none = document.createElement('li');
  none.className = 'tbm-none tbm-hide';
  none.setAttribute('role', 'presentation');
  none.textContent = tx[1];
  ul.appendChild(none);
  m.none = none;
  ul.addEventListener('keydown', e => tbmKey(m, e));
  /* Avec un champ de recherche, toucher un choix ne prend pas le focus : le clavier virtuel reste ouvert jusqu'au choix */
  const keepFocus = e => { if (m.search && e.target.closest && e.target.closest('.tbm-opt, .tbm-group')) e.preventDefault(); };
  ul.addEventListener('mousedown', keepFocus);
  ul.addEventListener('pointerdown', keepFocus);
  ul.addEventListener('click', e => {
    const li = e.target.closest ? e.target.closest('.tbm-opt') : null;
    if (!li || li.getAttribute('aria-disabled') === 'true') return;
    tbmChoose(m, Number(li.getAttribute('data-i')));
  });
  ul.addEventListener('mousemove', e => {
    const li = e.target.closest ? e.target.closest('.tbm-opt') : null;
    if (!li || li.getAttribute('aria-disabled') === 'true') return;
    const k = Number(li.getAttribute('data-i'));
    if (k !== m.active) tbmSetActive(m, k, false);
  });
  document.body.appendChild(ul);
  m.panel = ul;
  m.w0 = window.innerWidth;
  TBM.cur = m;
  m.btn.classList.add('tbm-trigger-open');
  m.btn.setAttribute('aria-expanded', 'true');
  tbmPlace(m);
  let k0 = sel.selectedIndex;
  if (k0 < 0 || (opts[k0] && opts[k0].disabled)) k0 = tbmFirst(m, 1);
  tbmSetActive(m, k0, 'center');
  (m.search || ul).focus({ preventScroll: true });
}

/* La saisie masque les choix dont le libellé ne contient pas le texte ; le premier choix visible devient le choix
   courant (Entrée le prend) ; aucun choix : « Aucun résultat ». */
function tbmFilter(m, q) {
  if (!m.panel) return;
  const nq = tbmNorm(q.trim()), opts = m.sel.options;
  let first = -1, vis = 0;
  for (let k = 0; k < m.lis.length; k++) {
    const hide = nq !== '' && m.norm[k].indexOf(nq) < 0;
    if (hide !== m.lis[k].classList.contains('tbm-hide')) m.lis[k].classList.toggle('tbm-hide', hide);
    if (!hide) { vis++; if (first < 0 && !opts[k].disabled) first = k; }
  }
  m.none.classList.toggle('tbm-hide', vis > 0);
  for (const g of (m.grps || [])) {   /* un titre dont aucune option du groupe n'est visible est masqué */
    let any = false;
    for (let k = g.first; k <= g.last; k++) if (!m.lis[k].classList.contains('tbm-hide')) { any = true; break; }
    if (any === g.li.classList.contains('tbm-hide')) g.li.classList.toggle('tbm-hide', !any);
  }
  m.panel.scrollTop = 0;
  tbmPlace(m);
  if (nq === '') {
    let k0 = m.sel.selectedIndex;
    if (k0 < 0 || (opts[k0] && opts[k0].disabled)) k0 = tbmFirst(m, 1);
    tbmSetActive(m, k0, 'center');
  } else tbmSetActive(m, first, true);
}

/* Sous le bouton (4 px), bord gauche aligné, au moins aussi large, à 8 px au moins des bords de la fenêtre ;
   dessous si elle y tient entière, sinon dessus si la place y est plus grande (classe tbm-up). */
function tbmPlace(m) {
  const r = m.btn.getBoundingClientRect();
  m.x0 = r.left; m.y0 = r.top;
  tbmPlaceAt(m.panel, r);
}

/* p : la liste (position: fixed), r : le rectangle de son bouton. Sert aussi aux listes à types du Ground Unit Swapper. */
function tbmPlaceAt(p, r) {
  const vv = window.visualViewport, vw = document.documentElement.clientWidth;
  const vh = vv ? Math.min(window.innerHeight, vv.offsetTop + vv.height) : window.innerHeight;
  const cap = Math.min(0.62 * vh, 440);
  const below = vh - (r.bottom + 4) - 12, above = (r.top - 4) - 12;
  p.style.minWidth = Math.min(Math.max(180, r.width), vw - 16) + 'px';
  p.style.maxHeight = 'none';
  const up = Math.min(p.offsetHeight, cap) > below && above > below;
  p.style.maxHeight = Math.max(60, Math.min(cap, up ? above : below)) + 'px';
  p.classList.toggle('tbm-up', up);
  p.style.top = (up ? r.top - 4 - p.offsetHeight : r.bottom + 4) + 'px';
  p.style.left = r.left + 'px';
  const fw = p.getBoundingClientRect().width;
  let fl = r.left;
  if (fl + fw > vw - 8) fl = vw - 8 - fw;
  if (fl < 8) fl = 8;
  p.style.left = fl + 'px';
}

function tbmOk(m, k) {
  const o = m.sel.options[k], li = m.lis[k];
  return !!o && !o.disabled && !!li && !li.classList.contains('tbm-hide');
}

function tbmFirst(m, d) {
  const n = m.sel.options.length;
  let k = d > 0 ? 0 : n - 1;
  for (; k >= 0 && k < n; k += d) if (tbmOk(m, k)) return k;
  return -1;
}

function tbmSetActive(m, k, reveal) {
  const p = m.panel;
  if (!p) return;
  if (m.actLi) m.actLi.classList.remove('active');
  m.active = k;
  const li = k >= 0 ? m.lis[k] : null;
  m.actLi = li || null;
  if (!li) { p.removeAttribute('aria-activedescendant'); return; }
  li.classList.add('active');
  p.setAttribute('aria-activedescendant', li.id);
  if (!reveal) return;
  const sh = m.searchBox ? m.searchBox.offsetHeight : 0;
  const pv = li.previousElementSibling;
  const t = (pv && pv.classList.contains('tbm-group') && !pv.classList.contains('tbm-hide') ? pv : li).offsetTop, h = li.offsetTop + li.offsetHeight - t;
  if (k === tbmFirst(m, 1) && !m.search) p.scrollTop = 0;
  else if (t - sh < p.scrollTop) p.scrollTop = Math.max(0, t - sh);
  else if (t + h > p.scrollTop + p.clientHeight) p.scrollTop = reveal === 'center' ? Math.max(0, t - (p.clientHeight - h) / 2) : t + h - p.clientHeight;
  if (m.searchBox && p.scrollTop > 0) {   /* le champ collé couvre le haut : le choix ne passe jamais dessous (le remplissage de la liste y compte) */
    const over = m.searchBox.getBoundingClientRect().bottom - li.getBoundingClientRect().top;
    if (over > 0.5) p.scrollTop = Math.max(0, p.scrollTop - over);
  }
}

function tbmStep(m, d) {
  const n = m.sel.options.length;
  for (let k = m.active + d; k >= 0 && k < n; k += d) {
    if (tbmOk(m, k)) { tbmSetActive(m, k, true); return; }
  }
}

/* Saisie de lettres (liste sans champ de recherche) : première option qui commence par elles, remise à zéro après 0,7 s */
function tbmType(m, ch) {
  clearTimeout(m.typeTimer);
  m.type += ch.toLowerCase();
  m.typeTimer = setTimeout(() => { m.type = ''; }, 700);
  const o = m.sel.options;
  for (let k = 0; k < o.length; k++) {
    if (tbmOk(m, k) && o[k].label.toLowerCase().indexOf(m.type) === 0) { tbmSetActive(m, k, true); return; }
  }
}

function tbmKey(m, e) {
  const k = e.key, inInput = !!(e.target && e.target.tagName === 'INPUT');
  if (k === 'ArrowDown' || k === 'ArrowUp') { e.preventDefault(); tbmStep(m, k === 'ArrowDown' ? 1 : -1); }
  else if (k === 'Home' && !inInput) { e.preventDefault(); tbmSetActive(m, tbmFirst(m, 1), true); }
  else if (k === 'End' && !inInput) { e.preventDefault(); tbmSetActive(m, tbmFirst(m, -1), true); }
  else if (k === 'Enter' || (k === ' ' && !inInput)) { e.preventDefault(); if (m.active >= 0) tbmChoose(m, m.active); }
  else if (k === 'Escape') { e.preventDefault(); e.stopPropagation(); tbmClose(true); }
  else if (k === 'Tab') { tbmClose(true); }   /* sans preventDefault : le focus part du bouton vers le contrôle suivant */
  else if (!inInput && k.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) { e.preventDefault(); tbmType(m, k); }
}

/* Choisir : si la valeur change, le <select> la prend et reçoit input puis change (qui bouillonnent), comme le contrôle natif */
function tbmChoose(m, k) {
  const sel = m.sel, o = sel.options[k];
  if (!o || o.disabled) return;
  const changed = k !== sel.selectedIndex;
  tbmClose(true);
  if (!changed) return;
  sel.selectedIndex = k;
  sel.dispatchEvent(new Event('input', { bubbles: true }));
  sel.dispatchEvent(new Event('change', { bubbles: true }));
}

function tbmClose(refocus) {
  const m = TBM.cur;
  if (!m) return;
  TBM.cur = null;
  clearTimeout(m.typeTimer);
  m.type = '';
  if (m.panel) m.panel.remove();
  m.panel = null;
  m.active = -1;
  m.actLi = null;
  m.lis = [];
  m.norm = [];
  m.search = null;
  m.searchBox = null;
  m.btn.classList.remove('tbm-trigger-open');
  m.btn.setAttribute('aria-expanded', 'false');
  if (refocus) m.btn.focus({ preventScroll: true });
}

/* Un toucher ou un clic hors de la liste et du bouton la ferme, sans agir ailleurs (le clic qui suit est avalé) ;
   le bouton d'une autre liste ferme celle-ci et s'ouvre ensuite par son propre clic. */
function tbmOutside(e) {
  const m = TBM.cur;
  if (!m) return;
  const t = e.target;
  if (m.panel.contains(t) || m.btn.contains(t)) return;
  const other = t && t.closest ? t.closest('.tbm-trigger') : null;
  tbmClose(false);
  if (other) return;
  TBM.swallow = true;
  const rel = () => { document.removeEventListener('pointerup', rel, true); document.removeEventListener('pointercancel', rel, true); setTimeout(() => { TBM.swallow = false; }, 350); };
  document.addEventListener('pointerup', rel, true);
  document.addEventListener('pointercancel', rel, true);
}

function tbmSwallowClick(e) {
  if (!TBM.swallow) return;
  TBM.swallow = false;
  e.stopPropagation();
  e.preventDefault();
}

/* Un changement de hauteur seul (clavier tactile ouvert sur le champ de recherche) replace la liste ; sinon elle se ferme */
function tbmResized() {
  const m = TBM.cur;
  if (!m) return;
  if (m.search && window.innerWidth === m.w0) tbmPlace(m);
  else tbmClose(false);
}

/* Le clavier virtuel change la zone visible sans toujours changer window.innerHeight : la liste ouverte est replacée */
function tbmViewport() {
  const m = TBM.cur;
  if (m && m.panel && window.innerWidth === m.w0) tbmPlace(m);
}

/* Le défilement de la page déplace le bouton : la liste se ferme */
function tbmScrolled(e) {
  const m = TBM.cur;
  if (!m || !m.panel) return;
  if (e.target === m.panel || (e.target.nodeType && m.panel.contains(e.target))) return;
  const r = m.btn.getBoundingClientRect();
  if (Math.abs(r.left - m.x0) > 0.5 || Math.abs(r.top - m.y0) > 0.5) tbmClose(false);
}
"""


def build_block():
    """Le texte du bloc, délimité par ses deux commentaires, avec un saut de ligne final."""
    return BLOCK_BEGIN + _JS + BLOCK_END + '\n'
