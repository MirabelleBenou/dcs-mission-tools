# DCS Ground Unit Swapper — Documentation technique

## 1. Vue d'ensemble

Application HTML monofichier offline (~220 Ko). Permet d'éditer en masse le **type** et le **skill** des unités au sol (`vehicle`) d'un fichier `.miz` DCS World, directement dans le navigateur, sans aucun envoi réseau. Fait partie de la **DCS Mission Suite** aux côtés du Briefing Generator (v2.1.1) et du Comm Plan Editor (v1.0.0).

**Cas d'usage cible :** un mission maker veut remplacer les 39 Hawk LN de Foothold par des S-300PS 5P85D LN, passer toutes les unités blindées à skill Excellent, ou préparer un swap de composition tactique avant une session de vol.

**Ce que l'outil fait :**
- Parse le fichier `mission` (Lua) contenu dans le `.miz`
- Extrait toutes les unités de la catégorie `vehicle` (unités au sol)
- Présente un tableau filtrable et triable de 877 lignes (sur Foothold SY)
- Permet le swap de type et/ou skill unitaire ou en masse (bulk edit)
- Applique les modifications par patch chirurgical (sans réécrire le fichier entier)
- Reconstruit le `.miz` et déclenche le téléchargement
- Supporte l'export/import JSON des modifications en attente

**Ce que l'outil ne fait pas :**
- Éditer les slots Client ou Player (exclus à l'extraction)
- Éditer les unités aériennes, navales, ou les objets statiques
- Modifier les noms de groupes ou d'unités (LECTURE SEULE — dépendances CTLD/MOOSE)
- Ajouter ou supprimer des unités
- Introduire des types absents du `.miz` chargé (restreint à la liste des types détectés)

**Fichier livrable :** `dcs_ground_unit_swapper_v1.3.0.html`

---

## 2. Démarrage rapide

### Charger une mission

Glisser-déposer un `.miz` sur la zone de dépôt, ou cliquer pour ouvrir le sélecteur de fichiers. Le fichier reste strictement local.

Après chargement (~1 à 2 secondes selon la taille du `.miz`) :
- Le nom du fichier apparaît en haut à droite du header
- Le tableau s'affiche avec toutes les unités au sol
- Les filtres et la barre de bulk edit deviennent actifs

### Naviguer et filtrer

- **Coalition** : Blue / Red / Neutrals
- **Groupe** / **Unité** : autocomplétion par datalist natif
- **Type actuel** : autocomplétion avec displayName
- **Familles** : chips à cliquer (Blindé, SAM, Artillerie, etc.)
- **Recherche libre** : filtre sur groupName + name + type en substring
- **Modifiées uniquement** : visible uniquement quand des modifications sont en attente ; filtre le tableau sur les unités modifiées, combinable avec tous les autres filtres en AND

Le compteur de modifications et les boutons d'action (charger un autre .miz, export/import JSON, sauvegarder) sont regroupés dans une **barre sticky en bas d'écran** (`#modifications-bar`), visible dès qu'un .miz est chargé. Le compteur affiche `N modification(s)` en ambre.

### Modifier le type d'une unité

Cliquer sur la cellule "Nouveau type" → combobox custom avec recherche (taper "300" pour les S-300PS, "Abrams" pour les Abrams, etc.). La cellule devient ambre si modifiée. Un bouton `↺` apparaît pour annuler.

### Modifier le skill d'une unité

Menu déroulant natif : Average / Good / High / Excellent. Bouton `↺` pour annuler.

### Bulk edit

1. Sélectionner des lignes (checkbox individuelle ou `Shift+click`)
2. Dans la barre bulk : choisir "Remplacer [type X] par [type Y]" et/ou "Skill = [valeur]"
3. `bulk-type-from` ne propose que les types **visibles** dans la vue actuelle (avec compteur "X visibles")
4. `bulk-type-to` propose le catalogue complet des types du miz (indépendant des filtres)
5. Cliquer **Appliquer**

### Sauvegarder

Le bouton **💾 Sauvegarder** génère un `.miz` nommé `{original}_swapped_{YYYYMMDD-HHmmss}.miz` et déclenche le téléchargement. L'état UI est préservé après sauvegarde — aucun rechargement nécessaire.

### Export / Import JSON

- **📥 Export JSON** : exporte les modifications en attente dans un `.json` horodaté
- **📤 Import JSON** : importe un fichier exporté précédemment, avec vérification du `mizFilename` et warning si différent. Les unités sont retrouvées par `unitId`. Les entrées inconnues sont ignorées avec compteur.

---

## 3. Architecture

```
[.miz] → JSZip → fichier "mission" (Lua UTF-8)
            ↓
        DCS_TOKENIZER.tokenize → tokens avec positions (offset/line/col)
            ↓
        DCS_PARSER.parse → AST avec pos sur chaque nœud
            ↓
        extractGroundUnits() → Array<UnitRecord>
            ↓
        UI_STATE.model (units, indices, source)
            ↓
        UI : tableau filtrable, comboboxes, bulk edit
            ↓
        Éditions → UI_STATE.edits (Map<unitId, { newType?, newSkill? }>)
            ↓
        Save → collectSwapPatches() → tri offset décroissant
            ↓
        applyPatches(source._text) → patchedSrc
            ↓
        retokenizeSafety(patchedSrc) (filet anti-régression)
            ↓
        JSZip + otherFiles intacts → Blob
            ↓
        Download {original}_swapped_{ts}.miz
```

**Note :** le parser DCS (tokenizer + parser + applyPatches + retokenizeSafety) est **copié à l'identique** depuis le Comm Plan Editor v2 phase1C. Aucune modification. Principe Mission Suite : chaque outil est un monofichier HTML autonome avec son propre exemplaire du parser.

---

## 4. Modèle de données

### UnitRecord

```javascript
{
  unitId:    number,   // identifiant numérique DCS
  name:      string,   // nom de l'unité (LECTURE SEULE)
  groupId:   number,
  groupName: string,   // nom du groupe (LECTURE SEULE)
  coalition: 'blue' | 'red' | 'neutrals',
  country:   string,
  type:      string,   // type DCS, ex: "Hawk ln"
  skill:     string,   // "Average" | "Good" | "High" | "Excellent"
  livery_id: string?,  // conservé, non édité
  family:    string,   // classification locale (voir FAMILY_MAP)
  typePos:   { start: {offset, line, col}, end: {...} },   // pour patch
  skillPos:  { start: {offset, line, col}, end: {...} },   // pour patch
}
```

### UI_STATE

```javascript
{
  model:           { units, indices, source, excludedCount },
  unitsById:       Map<unitId, UnitRecord>,
  edits:           Map<unitId, { newType?: string, newSkill?: string }>,
  filtered:        UnitRecord[],       // vue actuelle (après filtres + tri)
  selected:        Set<unitId>,        // lignes cochées
  sortCol:         string,
  sortDir:         'asc' | 'desc',
  lastChkIdx:      number | null,      // pour Shift+click
  famFilter:       Set<familyKey>,     // familles actives
  showModifiedOnly: boolean,
  bulkFromCombobox: Combobox | null,
  bulkToCombobox:   Combobox | null,
}
```

### Format indices

```javascript
model.indices = {
  coalitions: { blue: N, red: N, neutrals: N },
  families:   { armor: N, sam: N, ... },
  types:      Map<typeName, count>,
  groupNames: Set<string>,
  unitNames:  Set<string>,
}
```

---

## 5. Pipeline parser → patch

### Extraction (extractGroundUnits)

Traversée de l'AST depuis `mission.coalition.[blue|red|neutrals].country.[N].vehicle.group.[N].units.[N]`.

Exclusions :
- `skill == "Client"` ou `"Player"` → comptabilisé dans `excludedCount`, jamais affiché
- Unités sans champ `type` → ignorées silencieusement

Pour chaque unité retenue : lecture de `typePos` et `skillPos` (positions sources dans le texte Lua). Ces positions sont indispensables pour le patch chirurgical.

### Sérialisation (collectSwapPatches)

```javascript
function collectSwapPatches(edits, unitsById) {
  const patches = [];
  for (const [unitId, edit] of edits.entries()) {
    const unit = unitsById.get(unitId);
    if (edit.newType  !== undefined) patches.push({ pos: unit.typePos,  newValueStr: '"' + edit.newType  + '"' });
    if (edit.newSkill !== undefined) patches.push({ pos: unit.skillPos, newValueStr: '"' + edit.newSkill + '"' });
  }
  patches.sort((a, b) => b.pos.start.offset - a.pos.start.offset); // décroissant !
  return patches;
}
```

Le tri décroissant est critique : appliquer un patch modifie la longueur du fichier et invalide tous les offsets suivants. En partant de la fin du fichier, les offsets non encore traités restent valides.

---

## 6. Composants Combobox

### Combobox (instances indépendantes)

Utilisé pour `bulk-type-from` et `bulk-type-to`. Chaque instance possède son propre popup DOM embarqué dans le container.

```javascript
const combo = new Combobox(rootElement, {
  options:     [{ value: 'Hawk ln', label: 'Hawk ln — SAM Hawk LN M192 (39 visibles)' }],
  value:       '',
  placeholder: '— (inchangé)',
  emptyLabel:  '— (inchangé)',
});
combo.getValue();          // → '' ou 'Hawk ln'
combo.setValue('Hawk ln'); // → déclenche 'change'
combo.setOptions([...]);   // → préserve la valeur si toujours présente, revient à '' sinon
combo.destroy();
```

**Recherche :** substring insensible à la casse sur le `label` complet (type DCS + displayName + compteur). Taper "Abrams" matche "M-1 Abrams — MBT M1A2 Abrams".

**Navigation clavier :** `↓ ↑ Enter Escape Tab`.

### SharedCombobox (popup partagé)

Utilisé pour les 877 cellules "Nouveau type" du tableau. Un seul popup DOM dans `document.body`, ancré dynamiquement via `getBoundingClientRect() + position: fixed`.

```javascript
SharedCombobox.openOn(cellEl, {
  initialValue: currentType,
  onChange: (newValue) => { /* mise à jour de l'état */ },
});
SharedCombobox.setOptions(options); // appelé au chargement du miz
SharedCombobox.close();
```

**Gain DOM :** 877 cellules × 155 `<option>` = **135 935 nœuds** en v1.0.0 → **1 754 spans légers** en v1.1.0+ (gain ×77).

**Point critique — ordre d'appel dans `_select`** : le callback `onChange` doit être capturé dans une variable locale *avant* d'appeler `_close()`, car `_close()` met `_onChange = null`. Le pattern correct :

```javascript
function _select(value) {
  _currentVal = value;
  const cb = _onChange;   // capture avant _close()
  _close();
  if (cb) cb(value);      // jamais null ici
}
```

Ne pas inverser l'ordre : appeler `_close()` puis `_onChange(value)` conduit à un callback silencieusement ignoré (bug v1.1.0–v1.3.0, corrigé en v1.3.0 patch 1.3.2).

### Couplage filtre → bulk-type-from

`updateBulkFromOptions(rows)` est appelée dans `applyFiltersAndRender()` après calcul de `UI_STATE.filtered`. Elle calcule les types présents dans les lignes visibles avec leur compteur, et appelle `bulkFromCombobox.setOptions()`. Si la valeur sélectionnée n'est plus présente dans la nouvelle liste, elle revient à `''` automatiquement.

---

## 7. Table FAMILY_MAP

Classification statique embarquée de 155 types en 9 familles :

| Famille | CSS class | Nb types | Exemples |
|---|---|---|---|
| `armor` | `.fam-armor` | 36 | M-1 Abrams, T-72B3, BMP-2, Leopard-2 |
| `arti` | `.fam-arti` | 18 | Grad-URAL, SAU Gvozdika, MLRS, Scud_B |
| `sam` | `.fam-sam` | 40 | Hawk ln, S-300PS 5P85D ln, Patriot ln, Tor 9A331 |
| `radar` | `.fam-radar` | 16 | 1L13 EWR, Hawk sr, SA-11 Buk SR 9S18M1 |
| `aaa` | `.fam-aaa` | 13 | Gepard, ZSU-23-4 Shilka, ZSU_57_2 |
| `logi` | `.fam-logi` | 14 | M 818, KAMAZ Truck, Ural-375, ATZ-10 |
| `inf` | `.fam-inf` | 12 | Soldier M4, Infantry AK, JTAC |
| `infra` | `.fam-infra` | 3 | Ural-375 PBU, ZIL-131 KUNG, outpost |
| `unknown` | `.fam-unknown` | — | tout type absent de la table |

Fallback : `getFamily(type)` retourne `'unknown'` si le type n'est pas dans `FAMILY_MAP`.

---

## 8. DISPLAY_NAMES

Source : `object_db_v2_index.json` (mrSkortch ScriptsDatabase), 620 entrées.

Embarqué comme const JS dans le `<script>` principal :
```javascript
const DISPLAY_NAMES = {
  "Hawk ln": "SAM Hawk LN M192",
  "M-1 Abrams": "MBT M1A2 Abrams",
  // ... 620 entrées (~23 Ko)
};
function getDisplayName(type) { return DISPLAY_NAMES[type] || 'Inconnu'; }
```

Utilisations :
- Colonne "Type actuel" du tableau : type en texte normal + displayName en dessous (petits caractères, couleur dim)
- Labels des comboboxes : `"type — displayName (N visibles)"` (la recherche substring matche les deux)
- Datalist `#filter-type` : label enrichi avec displayName

---

## 9. Format export JSON

```json
{
  "format": "dcs-ground-unit-swapper-edits",
  "version": 1,
  "mizFilename": "Foothold_SY_extended_3_7_0_Coldwar_4thVEAW_v5.miz",
  "exportedAt": "2026-05-23T14:32:00.000Z",
  "edits": [
    { "unitId": 151, "name": "blueArmor-2", "groupName": "blueArmor",
      "newType": "M1A2C_SEP_V3", "newSkill": "Excellent" },
    { "unitId": 152, "name": "Alpha-1", "groupName": "SAM Alpha",
      "newType": "S-300PS 5P85D ln" }
  ]
}
```

**Import :** vérification de `format` (refus si différent), avertissement si `mizFilename` diffère du miz chargé (proceed ou cancel), lookup par `unitId` (non par nom), entrées inconnues ignorées avec compteur.

---

## 10. Limitations connues

- Les types proposés sont limités aux types **présents dans le `.miz` chargé**. Pour introduire un type absent, utiliser le Mission Editor de DCS.
- `livery_id` est préservé tel quel pour chaque unité (non éditable en UI).
- Les noms de groupes et d'unités sont en LECTURE SEULE (dépendances scripts CTLD/MOOSE qui les référencent par nom).
- Catégorie `vehicle` uniquement — exclut `plane`, `helicopter`, `ship`, `static`.
- Unités `skill == "Client"` ou `"Player"` exclues à l'extraction.

---

## 11. Glossaire

| Terme | Définition |
|---|---|
| `.miz` | Archive ZIP contenant `mission` (Lua), `options`, `warehouses`, assets audio/Lua |
| `vehicle` | Catégorie DCS pour les unités au sol motorisées |
| `unitId` | Identifiant numérique unique d'une unité dans le `.miz` |
| `groupId` | Identifiant numérique du groupe contenant l'unité |
| `skill` | Niveau de difficulté IA : Average / Good / High / Excellent / Client / Player |
| `typePos` / `skillPos` | Positions sources (offset, line, col) du champ dans le texte Lua |
| Patch chirurgical | Remplacement ciblé d'une valeur par offset dans le texte source, sans réécriture globale |
| FAMILY_MAP | Table statique embarquée classifiant les types en 9 familles thématiques |
| DISPLAY_NAMES | Table de 620 entrées `type DCS → nom lisible` (source mrSkortch) |
| SharedCombobox | Instance de popup combobox partagée entre les 877 cellules du tableau |
