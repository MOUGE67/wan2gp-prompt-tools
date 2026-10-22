# Prompt Tools - plugin WanGP (by Mouge)
# Pack d'outils pour le prompt : bouton effacer (avec annulation) et compteur de
# fenêtres glissantes. Chaque outil s'active ou se désactive depuis le menu 🧰.
from shared.utils.plugins import WAN2GPPlugin

JS = r"""
;(function () {
  if (window.__mougePromptToolsLoaded) return;
  window.__mougePromptToolsLoaded = true;

  // ---------- Langue ----------
  const FR = /^fr\b/i.test(navigator.language || '');
  const T = FR ? {
    clear: 'Effacer le prompt', undo: 'Annuler l\'effacement',
    tools: 'Prompt Tools', toolClear: 'Bouton effacer 🗑', toolCounter: 'Compteur de fenêtres 🪟',
    legacy: 'ancien plugin installé, désactivé ici',
    windows: n => `${n} fenêtre${n > 1 ? 's' : ''} détectée${n > 1 ? 's' : ''}`,
    noMode: '(mode non lu : 1 ligne = 1 fenêtre supposé)',
    noSliding: 'Pas de fenêtres glissantes avec le réglage actuel : ',
    separate: n => `<b>${n} vidéos séparées</b> seront ajoutées à la file.`,
    single: 'tout le texte forme un seul prompt.',
    multiPW: (w, n) => `⚠ Fenêtre ${w} : ${n} lignes (OK en mode paragraphe, mais différent du format 1 ligne = 1 fenêtre)`,
    multiW: (w, n) => `⚠ Fenêtre ${w} : retour à la ligne détecté, elle sera coupée en ${n} fenêtres`,
    multiUnk: (w, n) => `⚠ Fenêtre ${w} : retour à la ligne détecté, elle risque d'être coupée en ${n} fenêtres`,
    orphan: (w, f) => `⚠ Fenêtre ${w} commence par « ${f}: » : ligne vide en trop ? Ce champ devrait sûrement rester avec la fenêtre précédente`,
    jump: 'Cliquer pour sélectionner la ligne concernée'
  } : {
    clear: 'Clear prompt', undo: 'Undo clear',
    tools: 'Prompt Tools', toolClear: 'Clear button 🗑', toolCounter: 'Window counter 🪟',
    legacy: 'old standalone plugin installed, disabled here',
    windows: n => `${n} window${n > 1 ? 's' : ''} detected`,
    noMode: '(setting not found: assuming 1 line = 1 window)',
    noSliding: 'No sliding windows with the current setting: ',
    separate: n => `<b>${n} separate videos</b> will be added to the queue.`,
    single: 'the whole text is one prompt.',
    multiPW: (w, n) => `⚠ Window ${w}: ${n} lines (fine in paragraph mode, but not the 1 line = 1 window format)`,
    multiW: (w, n) => `⚠ Window ${w}: line break detected, it will be split into ${n} windows`,
    multiUnk: (w, n) => `⚠ Window ${w}: line break detected, it may be split into ${n} windows`,
    orphan: (w, f) => `⚠ Window ${w} starts with "${f}:": extra empty line? This field probably belongs to the previous window`,
    jump: 'Click to select the line'
  };

  // ---------- Réglages (mémorisés dans le navigateur) ----------
  const KEY = 'mougePromptTools';
  let settings = {clear: true, counter: true};
  try { Object.assign(settings, JSON.parse(localStorage.getItem(KEY) || '{}')); } catch (e) {}
  function save() { try { localStorage.setItem(KEY, JSON.stringify(settings)); } catch (e) {} }
  // si les anciens plugins séparés sont encore installés, on évite les doublons
  const legacy = () => ({clear: !!window.__wangpClearPromptLoaded, counter: !!window.__wangpWindowCounterLoaded});
  const on = k => settings[k] && !legacy()[k];

  // ---------- Styles ----------
  const CSS = `
  .mpt-btn{background:none;border:1px solid var(--border-color-primary,#888);border-radius:6px;cursor:pointer;
    font-size:13px;line-height:1;padding:2px 6px;margin-left:6px;opacity:.75;vertical-align:middle}
  .mpt-btn:hover{opacity:1;background:var(--background-fill-secondary,#eee)}
  .mpt-btn.undo{border-color:#2563eb;color:#2563eb;opacity:1}
  .mpt-menu{position:fixed;z-index:9999;min-width:220px;padding:8px 10px;border-radius:8px;font-size:13px;
    background:var(--background-fill-primary,#fff);color:var(--body-text-color,#222);
    border:1px solid var(--border-color-primary,#ccc);box-shadow:0 6px 20px rgba(0,0,0,.25)}
  .mpt-menu b{display:block;margin-bottom:6px}
  .mpt-menu label{display:flex;align-items:center;gap:6px;margin:4px 0;cursor:pointer}
  .mpt-menu small{display:block;opacity:.6;margin:-2px 0 4px 22px}
  .mpt-wincount{font-size:12px;margin-top:4px;padding:4px 8px;border-radius:6px;
    background:var(--background-fill-secondary,#f3f4f6);color:var(--body-text-color,#222);line-height:1.5}
  .mpt-wincount b{font-weight:600}
  .mpt-wincount .ok{color:#16a34a}
  .mpt-wincount .warn{color:#d97706;cursor:pointer;display:block}
  .mpt-wincount .warn:hover{text-decoration:underline}
  .mpt-wincount .muted{opacity:.7}`;
  const style = document.createElement('style'); style.textContent = CSS; document.head.appendChild(style);

  // ---------- Outil 1 : bouton effacer ----------
  function setValue(input, value) {
    const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
    setter.call(input, value);
    input.dispatchEvent(new Event('input', {bubbles: true}));   // Gradio récupère la nouvelle valeur
    input.dispatchEvent(new Event('change', {bubbles: true}));
  }
  function makeClearButton(input) {
    const btn = document.createElement('button');
    btn.type = 'button'; btn.className = 'mpt-btn mpt-clear';
    let saved = null, timer = null;
    const reset = () => { saved = null; btn.textContent = '🗑'; btn.title = T.clear; btn.classList.remove('undo'); };
    reset();
    btn.addEventListener('click', e => {
      e.preventDefault(); e.stopPropagation();
      if (saved !== null) { setValue(input, saved); clearTimeout(timer); reset(); input.focus(); return; }
      if (!input.value) return;
      saved = input.value; setValue(input, ''); input.focus();
      btn.textContent = '↩'; btn.title = T.undo; btn.classList.add('undo');
      clearTimeout(timer); timer = setTimeout(reset, 8000);
    });
    return btn;
  }

  // ---------- Outil 2 : compteur de fenêtres ----------
  // Analyse pure : reproduit le découpage de WanGP (shared/utils/prompt_parser.py)
  function analyze(text, mode) {
    text = (text || '').replace(/\r\n?/g, '\n');
    if (text.startsWith('!enhanced!\n')) text = text.slice(11);
    const raw = text.split('\n');
    const paragraphs = [];          // [{lines:[{text, lineNo}]}]
    let cur = null;
    raw.forEach((l, i) => {
      if (l.trim().startsWith('#')) return;            // commentaires ignorés par WanGP
      if (!l.trim()) { cur = null; return; }
      if (!cur) { cur = {lines: []}; paragraphs.push(cur); }
      cur.lines.push({text: l.trim(), lineNo: i});
    });
    const lineCount = paragraphs.reduce((n, p) => n + p.lines.length, 0);
    const warnings = [];
    paragraphs.forEach((p, idx) => {
      if (p.lines.length > 1) warnings.push({kind: 'multiline', win: idx + 1, n: p.lines.length, lineNo: p.lines[1].lineNo});
      if (idx > 0 && /^(overall_soundscape|non_diegetic_music)\s*:/i.test(p.lines[0].text))
        warnings.push({kind: 'orphan', win: idx + 1, field: p.lines[0].text.split(':')[0], lineNo: p.lines[0].lineNo});
    });
    let count;
    if (mode === 'W') count = lineCount;
    else if (mode === 'PW') count = paragraphs.length;
    else count = paragraphs.length;                    // mode inconnu : convention 1 ligne = 1 fenêtre
    return {count, paragraphs: paragraphs.length, lines: lineCount, warnings, mode};
  }


  const MODE_LABEL = 'How to Process each Line of the Text Prompt';
  let lastMode = null;
  function readMode() {
    const spans = document.querySelectorAll('[data-testid="block-info"], label span');
    for (const s of spans) {
      if (!s.textContent.includes(MODE_LABEL)) continue;
      const block = s.closest('.block') || s.parentElement;
      const inp = block && block.querySelector('input');
      const v = inp ? inp.value : '';
      if (!v) continue;
      if (/Sliding Window/i.test(v)) lastMode = /Paragraph/i.test(v) ? 'PW' : 'W';
      else if (/Same Prompt/i.test(v)) lastMode = 'FG';
      else lastMode = /Paragraph/i.test(v) ? 'PG' : 'G';
      break;
    }
    return lastMode;
  }


  function selectLine(input, lineNo) {
    const lines = input.value.replace(/\r\n?/g, '\n').split('\n');
    let start = 0; for (let i = 0; i < lineNo; i++) start += lines[i].length + 1;
    input.focus(); input.setSelectionRange(start, start + lines[lineNo].length);
    const lh = parseFloat(getComputedStyle(input).lineHeight) || 18;
    input.scrollTop = Math.max(0, lineNo * lh - input.clientHeight / 2);
  }


  function renderCounter(box, input) {
    const mode = readMode();
    const key = (on('counter') ? '1' : '0') + '|' + mode + '|' + input.value;
    if (box.dataset.key === key) return;          // rien n'a changé : on ne redessine pas
    box.dataset.key = key;
    if (!on('counter') || !input.value.trim()) { box.hidden = true; return; }
    const r = analyze(input.value, mode);
    box.hidden = false; box.innerHTML = '';
    const head = document.createElement('div');
    if (mode && !mode.includes('W')) {
      const n = mode === 'G' ? r.lines : r.paragraphs;
      head.innerHTML = '🪟 <span class="muted">' + T.noSliding + (mode !== 'FG' && n > 1 ? T.separate(n) : T.single) + '</span>';
      box.append(head); return;
    }
    head.innerHTML = '🪟 <b>' + T.windows(r.count) + '</b>' +
      (r.warnings.length ? '' : ' <span class="ok">✓</span>') +
      (mode ? '' : ' <span class="muted">' + T.noMode + '</span>');
    box.append(head);
    r.warnings.forEach(w => {
      const d = document.createElement('span'); d.className = 'warn';
      if (w.kind === 'multiline') d.textContent = (mode === 'PW' ? T.multiPW : mode === 'W' ? T.multiW : T.multiUnk)(w.win, w.n);
      else d.textContent = T.orphan(w.win, w.field);
      d.title = T.jump;
      d.addEventListener('click', () => selectLine(input, w.lineNo));
      box.append(d);
    });
  }

  // ---------- Menu 🧰 ----------
  let menu = null;
  function closeMenu() { if (menu) { menu.remove(); menu = null; } }
  function openMenu(anchor) {
    closeMenu();
    menu = document.createElement('div'); menu.className = 'mpt-menu';
    menu.innerHTML = `<b>🧰 ${T.tools}</b>`;
    [['clear', T.toolClear], ['counter', T.toolCounter]].forEach(([k, label]) => {
      const l = document.createElement('label');
      const cb = document.createElement('input'); cb.type = 'checkbox'; cb.checked = settings[k];
      const isLegacy = legacy()[k];
      cb.disabled = isLegacy;
      cb.addEventListener('change', () => { settings[k] = cb.checked; save(); refresh(); });
      l.append(cb, document.createTextNode(label)); menu.append(l);
      if (isLegacy) { const s = document.createElement('small'); s.textContent = T.legacy; menu.append(s); }
    });
    menu.addEventListener('click', e => e.stopPropagation());
    document.body.append(menu);
    const r = anchor.getBoundingClientRect();
    menu.style.top = (r.bottom + 6) + 'px';
    menu.style.left = Math.max(8, Math.min(r.left, window.innerWidth - menu.offsetWidth - 8)) + 'px';
  }
  document.addEventListener('click', closeMenu);
  window.addEventListener('scroll', closeMenu, true);

  // ---------- Montage dans l'interface ----------
  function hosts() {
    const set = new Set();
    document.querySelectorAll('.wangp-voice-prompt, #wangp-prompt-advanced, #wangp-prompt-wizard').forEach(h => set.add(h));
    return [...set];
  }
  function place(host, btn) {
    const label = host.querySelector('[data-testid="block-info"]');
    if (label) { label.append(btn); return; }
    if (getComputedStyle(host).position === 'static') host.style.position = 'relative';
    Object.assign(btn.style, {position: 'absolute', top: '4px', right: btn.classList.contains('mpt-tools') ? '40px' : '4px', zIndex: '20'});
    host.append(btn);
  }
  function refresh() {
    hosts().forEach(host => {
      const input = host.querySelector('textarea'); if (!input) return;
      // bouton effacer
      let clr = host.querySelector('.mpt-clear');
      if (on('clear') && !clr) place(host, makeClearButton(input));
      if (!on('clear') && clr) clr.remove();
      // menu + compteur : seulement sur le prompt principal
      if (host.id !== 'wangp-prompt-advanced') return;
      if (!host.querySelector('.mpt-tools')) {
        const t = document.createElement('button');
        t.type = 'button'; t.className = 'mpt-btn mpt-tools'; t.textContent = '🧰'; t.title = T.tools;
        t.addEventListener('click', e => { e.preventDefault(); e.stopPropagation(); menu ? closeMenu() : openMenu(t); });
        place(host, t);
      }
      let box = host.querySelector('.mpt-wincount');
      if (!box) {
        box = document.createElement('div'); box.className = 'mpt-wincount'; box.hidden = true;
        (input.closest('label') || input.parentElement).after(box);
        input.addEventListener('input', () => renderCounter(box, input));
      }
      renderCounter(box, input);
    });
  }

  let pending = false;
  new MutationObserver(() => {
    if (pending) return; pending = true;
    requestAnimationFrame(() => { pending = false; refresh(); });
  }).observe(document.body, {childList: true, subtree: true});
  refresh();
  setInterval(refresh, 1500);   // suit les changements de réglage et les prompts chargés
  console.log('[PromptTools] plugin loaded');
})();
"""


class PromptToolsPlugin(WAN2GPPlugin):
    def setup_ui(self):
        self.add_custom_js(JS)
