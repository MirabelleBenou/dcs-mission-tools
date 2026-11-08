#!/usr/bin/env python3
"""Bloc « MESSAGES DE LA SUITE » — une seule source pour les quatre outils et le shell de Mission Tools.

Rend le texte JavaScript du bloc : le toast, la fenêtre de confirmation et le sablier de la suite, et le CSS du bandeau.
Trois points d'entrée, et rien d'autre de public :
  - mtbToast(msg, type)                       type : success, info (défaut), warn, error ;
  - mtbConfirm({ title, text, ok, cancel })   rend une Promise<boolean> ;
  - mtbSpinner(msg) / mtbSpinnerHide().
Le bloc ne dépend d'aucune fonction de la page : les textes lui sont passés déjà traduits. Le CSS est dans le bloc
(chaîne injectée en tête du <head>) ; les éléments #mtb-toast, #mtb-modal et #mtb-spinner sont créés par le bloc en fin de
<body>. L'accent est la variable --accent, que chaque page pose dans son :root. Le bandeau (.mtb-banner.warn / .info) n'est
que du CSS : la page y pose ses propres éléments.
Le bloc est identique à l'octet dans les quatre modules et dans le shell construit : build_mission_tools.py le garde
(build en code 1 sinon).

Usage (par le build) : from messages_block import build_block ; texte = build_block()
"""

BLOCK_BEGIN = '/* ===== MESSAGES DE LA SUITE ===== */'
BLOCK_END = '/* ===== FIN DES MESSAGES ===== */'

_JS = r"""
/* Toast, fenêtre de confirmation, sablier : un seul jeu de boîtes pour toute la suite. Réglage de la page : variable
   --accent dans :root. Les textes arrivent déjà traduits. */
(function () {
  const MTB_CSS = `
/* ── toast de suite ── */
#mtb-toast { position: fixed; right: 16px; bottom: var(--mtb-bottom, 24px); z-index: 1500;
  max-width: 440px; display: flex; gap: 10px; align-items: flex-start;
  background: var(--surface); color: var(--text); border: 1px solid var(--border);
  border-left: 4px solid var(--mtb-c, var(--accent)); border-radius: 4px;
  padding: 10px 14px; font-size: 13px; line-height: 1.45; box-shadow: 0 4px 20px rgba(0,0,0,.5);
  opacity: 0; transform: translateY(8px); transition: opacity .2s, transform .2s; pointer-events: none; }
#mtb-toast.show { opacity: 1; transform: none; }
#mtb-toast.success { --mtb-c: var(--success); }
#mtb-toast.warn    { --mtb-c: var(--warn); }
#mtb-toast.error   { --mtb-c: var(--error); }
#mtb-toast .mtb-ico { flex-shrink: 0; }
@media (max-width: 560px) { #mtb-toast { left: 12px; right: 12px; max-width: none; } }
/* ── fenêtre de confirmation ── */
#mtb-modal { position: fixed; inset: 0; z-index: 2500; background: rgba(0,0,0,.6);
  display: none; align-items: center; justify-content: center; padding: 16px; }
#mtb-modal.open { display: flex; }
#mtb-modal .mtb-box { background: var(--surface); border: 1px solid var(--border); border-top: 3px solid var(--accent);
  border-radius: 4px; width: 100%; max-width: 460px; padding: 20px 22px 16px; box-shadow: 0 8px 32px rgba(0,0,0,.6); }
#mtb-modal h2 { font-size: 15px; font-weight: 600; color: var(--text); margin: 0 0 10px; }
#mtb-modal p { font-size: 13px; line-height: 1.55; color: var(--text-2); margin: 0 0 6px; }
#mtb-modal .mtb-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 18px; flex-wrap: wrap; }
#mtb-modal button { min-height: 44px; padding: 0 18px; border-radius: 4px; font: inherit; font-size: 13px; cursor: pointer; }
#mtb-modal .mtb-cancel { background: transparent; color: var(--text-dim); border: 1px solid var(--border); }
#mtb-modal .mtb-ok { background: var(--accent); color: #111; border: 1px solid var(--accent); font-weight: 600; }
#mtb-modal button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
/* ── bandeau ── */
.mtb-banner { display: flex; align-items: center; gap: 10px; padding: 6px 20px; font-size: 12px; line-height: 1.4; flex-shrink: 0; }
.mtb-banner.warn { background: #2A2200; border-bottom: 1px solid #5A4400; color: #FFD54F; }
.mtb-banner.info { background: color-mix(in srgb, var(--accent) 12%, var(--surface)); border-bottom: 1px solid color-mix(in srgb, var(--accent) 45%, transparent); color: var(--text); }
/* ── sablier ── */
#mtb-spinner { position: fixed; inset: 0; z-index: 2000; background: rgba(0,0,0,.7); display: none; align-items: center; justify-content: center; }
#mtb-spinner.open { display: flex; }
#mtb-spinner .mtb-sbox { background: var(--surface); border: 1px solid var(--accent); border-radius: 10px; padding: 32px 48px; text-align: center; }
#mtb-spinner .mtb-anim { width: 36px; height: 36px; border: 3px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: mtbspin .8s linear infinite; margin: 0 auto 16px; }
@keyframes mtbspin { to { transform: rotate(360deg); } }
#mtb-spinner .mtb-smsg { color: var(--text-dim); font-size: 13px; }
`;
  const MTB_ICON = { success: '✅', warn: '⚠️', error: '❌', info: '' };
  const MTB_MS = { success: 3000, info: 3000, warn: 4500, error: 6000 };
  let mtbTimer = null;
  let mtbClose = null;   /* ferme la fenêtre ouverte et rend son choix ; null si aucune n'est ouverte */
  let mtbToastEl = null, mtbModalEl = null, mtbSpinEl = null;

  function mtbMount() {
    const st = document.createElement('style');
    st.setAttribute('data-mtb', '');
    st.textContent = MTB_CSS;
    document.head.insertBefore(st, document.head.firstChild);
    const mk = html => { const d = document.createElement('div'); d.innerHTML = html.trim(); return d.firstChild; };
    mtbToastEl = document.body.appendChild(mk('<div id="mtb-toast" role="status" aria-live="polite"><span class="mtb-ico"></span><span class="mtb-txt"></span></div>'));
    mtbModalEl = document.body.appendChild(mk('<div id="mtb-modal" role="dialog" aria-modal="true" aria-labelledby="mtb-modal-title"><div class="mtb-box"><h2 id="mtb-modal-title"></h2><p></p><div class="mtb-actions"><button type="button" class="mtb-cancel"></button><button type="button" class="mtb-ok"></button></div></div></div>'));
    mtbSpinEl = document.body.appendChild(mk('<div id="mtb-spinner"><div class="mtb-sbox"><div class="mtb-anim"></div><div class="mtb-smsg"></div></div></div>'));
  }

  /* Un seul toast à la fois : le nouveau remplace l'ancien et relance la minuterie. Posé au-dessus de la barre du bas
     quand elle est affichée, à 24 px du bas sinon. Un saut de ligne du texte reste un saut de ligne. */
  function mtbShowToast(msg, type) {
    if (!Object.prototype.hasOwnProperty.call(MTB_MS, type)) type = 'info';
    const bar = document.getElementById('modifications-bar');
    const visible = !!bar && !bar.classList.contains('hidden') && bar.offsetHeight > 0;
    mtbToastEl.style.setProperty('--mtb-bottom', (visible ? bar.offsetHeight + 12 : 24) + 'px');
    mtbToastEl.querySelector('.mtb-ico').textContent = MTB_ICON[type];
    const txt = mtbToastEl.querySelector('.mtb-txt');
    txt.textContent = '';
    String(msg == null ? '' : msg).split('\n').forEach((line, i) => {
      if (i) txt.appendChild(document.createElement('br'));
      txt.appendChild(document.createTextNode(line));
    });
    mtbToastEl.className = 'show ' + type;
    clearTimeout(mtbTimer);
    mtbTimer = setTimeout(() => { mtbToastEl.className = ''; }, MTB_MS[type]);
  }

  /* Annuler, Échap ou un toucher sur le fond rendent false ; l'action rend true. Une fenêtre déjà ouverte rend false. */
  function mtbShowConfirm(o) {
    if (mtbClose) mtbClose(false);
    o = o || {};
    return new Promise(resolve => {
      const bOk = mtbModalEl.querySelector('.mtb-ok'), bNo = mtbModalEl.querySelector('.mtb-cancel');
      const before = document.activeElement;
      mtbModalEl.querySelector('h2').textContent = o.title || '';
      mtbModalEl.querySelector('p').textContent = o.text || '';
      bOk.textContent = o.ok || '';
      bNo.textContent = o.cancel || '';
      const done = v => {
        if (mtbClose !== done) return;
        mtbClose = null;
        mtbModalEl.classList.remove('open');
        document.removeEventListener('keydown', key, true);
        bOk.onclick = bNo.onclick = mtbModalEl.onclick = null;
        if (before && before.focus && document.contains(before)) { try { before.focus({ preventScroll: true }); } catch (e) {} }
        resolve(v);
      };
      const key = e => {
        if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); done(false); return; }
        if (e.key === 'Tab') {   /* le focus reste entre les deux boutons */
          const a = document.activeElement;
          if (e.shiftKey && a === bNo) { e.preventDefault(); bOk.focus(); }
          else if (!e.shiftKey && a === bOk) { e.preventDefault(); bNo.focus(); }
          else if (a !== bOk && a !== bNo) { e.preventDefault(); bOk.focus(); }
        }
      };
      mtbClose = done;
      bOk.onclick = () => done(true);
      bNo.onclick = () => done(false);
      mtbModalEl.onclick = e => { if (e.target === mtbModalEl) done(false); };
      document.addEventListener('keydown', key, true);
      mtbModalEl.classList.add('open');
      bOk.focus();
    });
  }

  function mtbShowSpinner(msg) {
    mtbSpinEl.querySelector('.mtb-smsg').textContent = msg || '';
    mtbSpinEl.classList.add('open');
  }
  function mtbHideSpinner() {
    mtbSpinEl.classList.remove('open');
  }

  if (document.body) mtbMount();
  else document.addEventListener('DOMContentLoaded', mtbMount);
  window.mtbToast = mtbShowToast;
  window.mtbConfirm = mtbShowConfirm;
  window.mtbSpinner = mtbShowSpinner;
  window.mtbSpinnerHide = mtbHideSpinner;
})();
"""


def build_block():
    """Le texte du bloc, délimité par ses deux commentaires, avec un saut de ligne final."""
    return BLOCK_BEGIN + _JS + BLOCK_END + '\n'
