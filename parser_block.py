#!/usr/bin/env python3
"""Bloc « PARSEUR DE LA SUITE » — une seule source pour le parseur des tables Lua et le contrôle d'après écriture des quatre
outils de Mission Tools.

Rend le texte JavaScript du bloc : `DCS_PARSER` (le parseur d'AST avec positions sources, qui suit la grammaire des tables de
Lua : aucun séparateur avant le premier champ, exactement un `,` ou `;` entre deux champs, au plus un après le dernier ; toute
autre suite lève une `ParseError`, au chargement comme après l'écriture) et `retokenizeSafety` (découpe le texte écrit, puis le
passe au parseur ; lève une erreur si l'un ou l'autre refuse). Le bloc s'appuie sur `DCS_TOKENIZER`, qui reste dans chaque
module, devant lui.
Le bloc est identique à l'octet dans les quatre modules : build_mission_tools.py le garde (build en code 1 sinon), et
tests/test_lua_separators.py le fait tourner sous Node.

Usage (par le build) : from parser_block import build_block ; texte = build_block()
"""

BLOCK_BEGIN = '/* ===== PARSEUR DE LA SUITE ===== */'
BLOCK_END = '/* ===== FIN DU PARSEUR ===== */'

_JS = r"""
// ═══════════════════════════════════════════════════════════════
// DCS_PARSER — AST avec positions sources, selon la grammaire des tables de Lua
//
// Chaque nœud porte pos = { start:{line,col,offset}, end:{line,col,offset} }
// (tous 0-based, end exclusif).
//
// Feuilles (number, string, bool, nil, ident) :
//   pos encadre la valeur brute — GUILLEMETS INCLUS pour les strings.
//   → lua.substring(pos.start.offset, pos.end.offset) redonne la valeur brute.
//
// Tables :
//   pos.start → '{', pos.end → après '}'.
//
// Paires (entries) :
//   entry.keyPos   → de '[' jusqu'après ']' (ou identifiant nu)
//   entry.valuePos → délégué à node.pos de la valeur
//
// Assignation racine :
//   pos couvre depuis 'mission' jusqu'après '}'.
//
// Séparateurs, comme Lua (fieldlist ::= field { fieldsep field } [ fieldsep ], fieldsep ::= ',' | ';') : aucun
// séparateur avant le premier champ ; exactement un entre deux champs ; au plus un après le dernier. Toute autre
// suite lève une ParseError.
// ═══════════════════════════════════════════════════════════════
const DCS_PARSER = (() => {

  class ParseError extends Error {
    constructor(msg, token) {
      super(msg);
      this.tokenLine   = token ? token.start.line + 1 : '?';
      this.tokenCol    = token ? token.start.col      : '?';
      this.tokenOffset = token ? token.start.offset   : '?';
    }
    toString() { return `ParseError L${this.tokenLine}:${this.tokenCol} — ${this.message}`; }
  }

  function parse(tokens) {
    const tks = tokens.filter(t => t.type !== 'COMMENT');
    let p = 0;

    function peek()    { return tks[p]; }
    function consume() { return tks[p++]; }

    function expect(type) {
      const tk = peek();
      if (!tk || tk.type !== type)
        throw new ParseError(
          `Attendu ${type}, obtenu ${tk ? tk.type + '(' + JSON.stringify(tk.value) + ')' : 'EOF'}`,
          tk
        );
      return consume();
    }

    // Construire un objet pos à partir de deux tokens de borne
    function makePos(startTk, endTk) {
      return {
        start: { line: startTk.start.line, col: startTk.start.col, offset: startTk.start.offset },
        end:   { line: endTk.end.line,     col: endTk.end.col,     offset: endTk.end.offset     }
      };
    }

    function parseValue() {
      const tk = peek();
      if (!tk || tk.type === 'EOF') throw new ParseError('Valeur attendue, EOF atteint', tk);

      if (tk.type === 'NUMBER') { consume(); return { kind:'number', value:tk.value, raw:tk.raw,   pos:makePos(tk,tk) }; }
      if (tk.type === 'STRING') { consume(); return { kind:'string', value:tk.value,                pos:makePos(tk,tk) }; }
      if (tk.type === 'BOOL')   { consume(); return { kind:'bool',   value:tk.value, raw:tk.raw,   pos:makePos(tk,tk) }; }
      if (tk.type === 'NIL')    { consume(); return { kind:'nil',                                   pos:makePos(tk,tk) }; }
      if (tk.type === 'LBRACE') { return parseTable(); }
      if (tk.type === 'IDENT')  { consume(); return { kind:'ident',  value:tk.value,               pos:makePos(tk,tk) }; }

      throw new ParseError(`Token inattendu comme valeur: ${tk.type}(${JSON.stringify(tk.value)})`, tk);
    }

    function parseTable() {
      const lbrace = expect('LBRACE');
      const entries = [];
      while (true) {
        const tk = peek();
        if (!tk || tk.type === 'RBRACE' || tk.type === 'EOF') break;
        entries.push(parseEntry());
        const sep = peek();
        if (sep && (sep.type === 'COMMA' || sep.type === 'SEMICOLON')) { consume(); continue; }
        // pas de séparateur : ce champ est le dernier, la table doit se fermer ici
        if (sep && sep.type !== 'RBRACE')
          throw new ParseError(`Séparateur « , » ou « ; » attendu entre deux champs, obtenu ${sep.type}(${JSON.stringify(sep.value)})`, sep);
        break;
      }
      const rbrace = expect('RBRACE');
      return { kind:'table', entries, pos: makePos(lbrace, rbrace) };
    }

    function parseEntry() {
      const tk = peek();

      // [N] = v  ou  ["clé"] = v
      if (tk.type === 'LBRACKET') {
        const lbrack = consume();
        const kt = peek();
        let key;
        if      (kt.type === 'NUMBER') { consume(); key = { kind:'int',    value:kt.value }; }
        else if (kt.type === 'STRING') { consume(); key = { kind:'string', value:kt.value }; }
        else throw new ParseError(`Clé invalide dans []: attendu NUMBER ou STRING, obtenu ${kt.type}`, kt);
        const rbrack = expect('RBRACKET');
        const keyPos = makePos(lbrack, rbrack);
        expect('EQ');
        const value = parseValue();
        return { key, keyPos, value, valuePos: value.pos };
      }

      // ident = v  (racine ou clé nue rare)
      if (tk.type === 'IDENT' && tks[p + 1] && tks[p + 1].type === 'EQ') {
        const it = consume();
        const key    = { kind:'ident', value:it.value };
        const keyPos = makePos(it, it);
        consume(); // EQ
        const value = parseValue();
        return { key, keyPos, value, valuePos: value.pos };
      }

      // Valeur sans clé (liste ordonnée)
      const value = parseValue();
      return { key:null, keyPos:null, value, valuePos: value.pos };
    }

    // Point d'entrée : "mission = { … }"
    const first = peek();
    let root;
    if (first.type === 'IDENT') {
      const nt = consume();
      expect('EQ');
      const value = parseValue();
      root = {
        kind: 'assignment', name: nt.value, value,
        pos:  { start: { line:nt.start.line, col:nt.start.col, offset:nt.start.offset },
                end:   value.pos.end }
      };
    } else if (first.type === 'LBRACE') {
      root = parseValue();
    } else {
      throw new ParseError(`Structure racine inattendue: ${first.type}`, first);
    }

    const eof = peek();
    if (eof.type !== 'EOF')
      throw new ParseError(`Contenu inattendu après table racine: ${eof.type}`, eof);

    return root;
  }

  return { parse, ParseError };
})();

// Contrôle d'après écriture : le texte se découpe, puis le parseur (grammaire des tables de Lua) l'accepte. Lève une
// erreur sinon ; l'appelant n'écrit alors rien.
function retokenizeSafety(patchedSrc) {
  const t0 = performance.now();
  const { tokens, errors } = DCS_TOKENIZER.tokenize(patchedSrc);
  const elapsed = Math.round(performance.now() - t0);
  if (errors.length > 0) {
    throw new Error('Retokenize failed: ' + errors[0].message + ' L' + (errors[0].line+1) + ':C' + (errors[0].col+1));
  }
  try {
    DCS_PARSER.parse(tokens);
  } catch (e) {
    throw new Error('Retokenize failed: ' + (e && e.message ? e.message : String(e)) + (e && e.tokenLine !== undefined ? ' L' + e.tokenLine + ':C' + (Number(e.tokenCol) + 1) : ''));
  }
  console.log('[Save] Retokenize OK : 0 erreurs, ' + tokens.length.toLocaleString() + ' tokens, ' + elapsed + ' ms');
}
"""


def build_block():
    """Le texte du bloc, délimité par ses deux commentaires, avec un saut de ligne final."""
    return BLOCK_BEGIN + _JS + BLOCK_END + '\n'
