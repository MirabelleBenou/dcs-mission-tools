#!/usr/bin/env python3
"""Bloc « TÉLÉPHONE » — une seule source pour les quatre outils de Mission Tools (pas pour le shell).

Rend le texte JavaScript du bloc : ce qui, sous 600 px de large, est commun aux quatre outils. Une seule condition,
(max-width: 600px), suivie en direct (rotation, téléphone pliable, fenêtre redimensionnée : aucune page n'est rechargée, rien
n'est perdu). Au-dessus de 600 px, le bloc ne change rien : ce qu'il ajoute est caché, et ce qu'il déplace est remis à sa place.
Il porte :
  - l'en-tête sur une ligne (CSS seul) : « ◄ » (44 × 44), sigle, nom du fichier, drapeau (44 × 44) ; le titre est caché ;
  - la rangée de pastilles #mph-chips, sous l'en-tête : une seule rangée, boutons de 44 px de haut ; le repli « Filtres (n) »
    (n = le nombre de filtres qui ne sont pas à leur valeur par défaut) ; les éléments propres à l'outil (compteur, onglets,
    pastille « En une fois ») y sont posés par l'outil lui-même, et rendus à leur place au-dessus de 600 px ;
  - la barre du bas sur une rangée : compteur, ⋯, « 💾 Sauvegarder » ; ⋯ ouvre au-dessus de la barre le menu des actions rares
    (le menu .mtb-menu du bloc des messages) : les boutons de la base y sont posés tels quels (même gestionnaire, même état
    désactivé, mêmes questions) et rendus à leur place au-dessus de 600 px ;
  - les cases à cocher de #main-ui à 44 × 44.
Points d'entrée, et rien d'autre de public (window.mph) :
  - mph.phone                      le MediaQueryList (max-width: 600px) ;
  - mph.row()                      la rangée #mph-chips (créée au premier appel, première de #main-ui) ;
  - mph.chip({ id, label, box, count })   la pastille de repli « Filtres (n) » : label est une clé de t() ; box l'élément
                                   replié sous 600 px tant que la pastille n'est pas dépliée ; count() rend n ;
  - mph.dock(el, { title })        pose un élément existant dans la rangée sous 600 px, et le remet à sa place au-dessus ;
                                   title : son texte complet devient son title (compteur raccourci) ;
  - mph.countOn(el, count)         ajoute « (n) » à une pastille existante ;
  - mph.count(box…)                n par défaut : listes hors de leur première option, recherche non vide, cases cochées ;
  - mph.refresh()                  recalcule les « (n) » ;
  - mph.on(fn)                     fn(téléphone: bool) à chaque passage du seuil, après la mise en place.
Les textes passent par t() : footer.more (les quatre outils), filter.title (CPE, LE : la pastille).
Le bloc est identique à l'octet dans les quatre modules : build_mission_tools.py le garde (build en code 1 sinon).

Usage (par le build) : from mobile_block import build_block ; texte = build_block()
"""

BLOCK_BEGIN = '/* ===== TELEPHONE (SOUS 600 PX) ===== */'
BLOCK_END = '/* ===== FIN DU TELEPHONE ===== */'

_JS = r"""
/* Téléphone : sous 600 px de large, l'en-tête sur une ligne, la rangée de pastilles, la barre du bas sur une rangée et son menu ⋯.
   Une condition, suivie en direct ; au-dessus, rien ne change. Les textes passent par t() (footer.more, filter.title). */
(function () {
  const mq = window.matchMedia('(max-width: 600px)');
  const byId = id => document.getElementById(id);
  const MPH_CSS = `
/* hors téléphone : ce que le bloc ajoute ne s'affiche pas */
#mph-chips, .mph-more, .mph-n { display: none; }
@media (max-width: 600px) {
  /* ── en-tête : une ligne, 56 px au plus ── */
  #app-header { flex-wrap: nowrap; align-items: center; gap: 8px; padding: 4px 8px; min-height: 0; }
  #app-header::after { display: none; }
  #app-header .header-title { display: none; }
  #app-header .mt-back-injected { order: 0; flex: 0 0 44px; box-sizing: border-box; width: 44px; min-width: 44px; height: 44px; min-height: 44px;
    margin: 0 !important; padding: 0 !important; font-size: 0 !important; letter-spacing: 0 !important; line-height: 1;
    display: inline-flex; align-items: center; justify-content: center; }
  #app-header .mt-back-injected::before { content: '◄'; content: '◄' / ''; font-size: 16px; line-height: 1; }
  #app-header .header-logo { order: 1; flex: 0 0 auto; }
  #app-header .header-miz { order: 2; flex: 1 1 0; min-width: 0; max-width: none; margin: 0; text-align: left;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  #app-header .header-lang-btn { order: 3; flex: 0 0 44px; box-sizing: border-box; width: 44px; height: 44px; min-width: 44px; min-height: 44px;
    margin: 0; padding: 0; }

  /* ── rangée de pastilles : une seule rangée, jamais à la ligne ── */
  #mph-chips { display: flex; flex-wrap: nowrap; align-items: center; gap: 8px; flex: 0 0 auto; box-sizing: border-box;
    padding: 6px 10px; background: var(--surface); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 30; }
  #mph-chips > button { display: inline-flex; flex: 0 0 auto; align-items: center; gap: 6px; box-sizing: border-box; width: auto; min-width: 0;
    min-height: 44px; margin: 0; padding: 0 12px; background: var(--surface-2); border: 1px solid var(--border); border-radius: 4px;
    color: var(--text); font: inherit; font-size: 13px; line-height: 1.2; text-align: left; white-space: nowrap; cursor: pointer; }
  #mph-chips > button[aria-expanded="true"] { border-color: var(--accent); color: var(--accent); }
  #mph-chips .mph-n { display: inline; color: var(--text-dim); }
  #mph-chips .mph-n.on { color: var(--accent); }
  #mph-chips > .display-count, #mph-chips > #filter-count { margin: 0 0 0 auto; padding: 0; border: 0; font-size: 12px; white-space: nowrap; }
  #mph-chips > #le-tabs { display: flex; position: static; flex: 0 1 auto; gap: 4px; margin: 0; padding: 0; border: 0; background: none; }
  #mph-chips > #le-tabs .le-tab { flex: 0 0 auto; min-height: 44px; padding: 0 12px; font-size: 13px; }
  [data-mph-fold]:not([data-mph-open]) { display: none !important; }

  /* ── barre du bas : compteur · ⋯ · Sauvegarder, une rangée de 60 px au plus ── */
  #modifications-bar { flex-wrap: nowrap; align-items: center; gap: 8px; padding: 6px 10px; }
  #modifications-bar #mod-count { flex: 0 1 auto; margin: 0; white-space: nowrap; }
  #modifications-bar > .mtb-menu-wrap:not(.mph-more), #modifications-bar > #btn-save-note { display: none; }
  #modifications-bar > .mph-more { display: inline-block; flex: 0 0 auto; }
  #modifications-bar > #btn-save { flex: 0 0 auto; margin-left: auto; min-height: 44px; white-space: nowrap; }
  .mph-more-btn { box-sizing: border-box; width: 44px; min-width: 44px; min-height: 44px; padding: 0; font-size: 20px; line-height: 1; text-align: center; }
  .mph-more-btn::after { content: none; }
  .mph-more .mtb-menu { min-width: 260px; }
  .mph-more .mtb-menu > hr { flex: 0 0 auto; margin: 0; border: 0; border-top: 1px solid var(--border); }

  /* ── cases à cocher : 44 × 44, la case dessinée au centre ── */
  #main-ui input[type="checkbox"] { -webkit-appearance: none; appearance: none; box-sizing: border-box; display: inline-grid; place-content: center;
    flex: none; width: 44px; height: 44px; min-width: 44px; min-height: 44px; margin: 0; padding: 0; background: transparent; border: 0; cursor: pointer; }
  #main-ui input[type="checkbox"]::before { content: ''; box-sizing: border-box; width: 20px; height: 20px; border: 2px solid var(--text-dim);
    border-radius: 3px; background: var(--surface-2); }
  #main-ui input[type="checkbox"]:checked::before { border-color: var(--accent); background: var(--accent) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 14 14'%3E%3Cpath d='M2 7.5l3.2 3.2L12 3.8' fill='none' stroke='%23111' stroke-width='2.2'/%3E%3C/svg%3E") center / 14px 14px no-repeat; }
  #main-ui input[type="checkbox"]:indeterminate::before { border-color: var(--accent); background: linear-gradient(var(--accent), var(--accent)) center / 10px 2px no-repeat, var(--surface-2); }
  #main-ui input[type="checkbox"]:disabled { opacity: .4; cursor: default; }
}
`;
  const items = [];          /* la rangée, dans l'ordre : { el, own, mark, title } */
  const counters = [];       /* les « (n) » : { span, count } */
  const menuNodes = [];      /* ce qui est posé dans ⋯ : { el, mark, addedRole } */
  const listeners = [];
  let row = null, moreBtn = null, moreMenu = null, raf = 0;

  function mphLabel() { return t('footer.more'); }

  /* ── ⋯ : le bouton et son menu, dans la barre du bas (cachés au-dessus de 600 px) ── */
  function buildMore() {
    const bar = byId('modifications-bar'), save = byId('btn-save');
    if (!bar || !save || moreBtn) return;
    const wrap = document.createElement('div');
    wrap.className = 'mtb-menu-wrap mph-more';
    moreBtn = document.createElement('button');
    moreBtn.type = 'button';
    moreBtn.id = 'mph-more';
    moreBtn.className = 'btn-footer mtb-menu-btn mph-more-btn';
    moreBtn.textContent = '⋯';
    moreBtn.setAttribute('aria-haspopup', 'menu');
    moreBtn.setAttribute('aria-expanded', 'false');
    moreMenu = document.createElement('div');
    moreMenu.className = 'mtb-menu';
    moreMenu.setAttribute('role', 'menu');
    moreMenu.hidden = true;
    wrap.appendChild(moreBtn);
    wrap.appendChild(moreMenu);
    bar.insertBefore(wrap, save);
    texts();
  }
  function texts() {
    if (!moreBtn) return;
    moreBtn.setAttribute('aria-label', mphLabel());
    moreBtn.title = mphLabel();
  }
  function closeMenu() {
    if (!moreMenu) return;
    moreMenu.hidden = true;
    moreBtn.setAttribute('aria-expanded', 'false');
  }
  /* Ce que ⋯ porte, dans l'ordre : Charger un autre .miz · le menu d'échange de l'outil · Tout annuler (un trait entre les groupes). */
  function menuPlan() {
    const bar = byId('modifications-bar'), out = [];
    const load = byId('btn-load-new');
    const exch = bar ? Array.prototype.slice.call(bar.querySelectorAll(':scope > .mtb-menu-wrap:not(.mph-more) > .mtb-menu > button')) : [];
    const undo = byId('btn-undo-all') || byId('btn-revert-all');
    if (load) out.push(load);
    if (exch.length) { out.push('hr'); exch.forEach(b => out.push(b)); }
    if (undo) { out.push('hr'); out.push(undo); }
    return out;
  }
  function dockMenu() {
    if (!moreMenu || menuNodes.length) return;
    menuPlan().forEach(n => {
      if (n === 'hr') {
        const hr = document.createElement('hr');
        hr.setAttribute('role', 'separator');
        moreMenu.appendChild(hr);
        menuNodes.push({ el: hr, mark: null, addedRole: false });
        return;
      }
      const mark = document.createComment('mph');
      n.parentNode.insertBefore(mark, n);
      const addedRole = n.getAttribute('role') === null;
      if (addedRole) n.setAttribute('role', 'menuitem');
      menuNodes.push({ el: n, mark, addedRole });
      moreMenu.appendChild(n);
    });
  }
  function undockMenu() {
    closeMenu();
    menuNodes.forEach(m => {
      if (!m.mark) { m.el.remove(); return; }
      m.mark.parentNode.insertBefore(m.el, m.mark);
      m.mark.remove();
      if (m.addedRole) m.el.removeAttribute('role');
    });
    menuNodes.length = 0;
  }

  /* ── la rangée de pastilles ── */
  function ensureRow() {
    if (row) return row;
    const main = byId('main-ui');
    if (!main) return null;
    row = document.createElement('div');
    row.id = 'mph-chips';
    main.insertBefore(row, main.firstChild);
    return row;
  }
  function plainText(el) { return (el.textContent || '').replace(/\s+/g, ' ').trim(); }
  function placeRow() {
    if (!row) return;
    items.forEach(i => {
      if (mq.matches) {
        if (!i.own && !i.mark) { i.mark = document.createComment('mph'); i.el.parentNode.insertBefore(i.mark, i.el); }
        row.appendChild(i.el);
        if (i.title) i.el.title = plainText(i.el);
      } else if (!i.own && i.mark) {
        i.mark.parentNode.insertBefore(i.el, i.mark);
        i.mark.remove();
        i.mark = null;
        if (i.title) i.el.removeAttribute('title');
      }
    });
  }
  function dock(el, o) {
    if (!el || !ensureRow() || items.some(i => i.el === el)) return;
    items.push({ el, own: false, mark: null, title: !!(o && o.title) });
    placeRow();
  }
  /* n par défaut : les listes hors de leur première option, les recherches non vides, les cases cochées, dans les éléments donnés. */
  function countIn() {
    let n = 0;
    Array.prototype.forEach.call(arguments, box => {
      if (!box) return;
      box.querySelectorAll('select').forEach(s => { if (s.value !== '') n++; });
      box.querySelectorAll('input[type="text"], input[type="search"]').forEach(i => { if (i.value.trim() !== '') n++; });
      box.querySelectorAll('input[type="checkbox"]').forEach(c => { if (c.checked) n++; });
    });
    return n;
  }
  function countOn(el, count) {
    if (!el) return;
    const span = document.createElement('span');
    span.className = 'mph-n';
    el.appendChild(document.createTextNode(' '));   /* « Filtres (n) » se lit aussi dans textContent */
    el.appendChild(span);
    counters.push({ span, count });
    refresh();
  }
  function chip(o) {
    if (!ensureRow() || !o.box) return null;
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'mph-chip';
    if (o.id) b.id = o.id;
    b.setAttribute('aria-expanded', 'false');
    const chev = document.createElement('span');
    chev.className = 'mtb-chev';
    chev.setAttribute('aria-hidden', 'true');
    const lab = document.createElement('span');
    lab.setAttribute('data-i18n', o.label);
    lab.textContent = t(o.label);
    b.appendChild(chev);
    b.appendChild(lab);
    o.box.setAttribute('data-mph-fold', '');
    b.addEventListener('click', () => {
      const open = !o.box.hasAttribute('data-mph-open');
      if (open) o.box.setAttribute('data-mph-open', ''); else o.box.removeAttribute('data-mph-open');
      b.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    items.push({ el: b, own: true, mark: null, title: false });
    row.appendChild(b);
    countOn(b, o.count);
    placeRow();
    return b;
  }
  function refresh() {
    counters.forEach(c => {
      let n = 0;
      try { n = c.count(); } catch (e) { n = 0; }
      const s = '(' + n + ')';
      if (c.span.textContent !== s) c.span.textContent = s;
      c.span.classList.toggle('on', n > 0);
    });
    if (mq.matches) items.forEach(i => { if (i.title && !i.own) { const s = plainText(i.el); if (i.el.title !== s) i.el.title = s; } });
  }
  function later() {
    if (raf) return;
    raf = requestAnimationFrame(() => { raf = 0; refresh(); });
  }

  function place() {
    placeRow();
    if (mq.matches) dockMenu(); else undockMenu();
    listeners.forEach(fn => { try { fn(mq.matches); } catch (e) { console.error(e); } });
  }
  function init() {
    const st = document.createElement('style');
    st.id = 'mph-style';
    st.textContent = MPH_CSS;
    document.head.appendChild(st);
    buildMore();
    place();
    if (mq.addEventListener) mq.addEventListener('change', place); else mq.addListener(place);
    ['input', 'change', 'click'].forEach(ev => document.addEventListener(ev, later, true));
    new MutationObserver(texts).observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
  }
  window.mph = {
    phone: mq,
    row: ensureRow,
    chip: chip,
    dock: dock,
    count: countIn,
    countOn: countOn,
    refresh: refresh,
    on: fn => { listeners.push(fn); }
  };
  if (document.body) init(); else document.addEventListener('DOMContentLoaded', init);
})();
"""


def build_block():
    """Le texte du bloc, délimité par ses deux commentaires, avec un saut de ligne final."""
    return BLOCK_BEGIN + _JS + BLOCK_END + '\n'
