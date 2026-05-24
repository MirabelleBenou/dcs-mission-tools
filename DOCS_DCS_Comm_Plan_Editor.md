# DCS Comm Plan Editor — Documentation technique

## 1. Vue d'ensemble

Application HTML monofichier offline (~120 Ko). Permet d'éditer les fréquences radio des slots **Client** d'un fichier `.miz` DCS World, directement dans le navigateur, sans aucun envoi réseau. Fait partie de la **DCS Mission Suite** aux côtés du Briefing Generator (v2.1.1) et du Ground Unit Swapper (v1.2.0).

**Cas d'usage cible :** un mission maker a configuré un plan de communication dans son `.miz` (fréquences par appareil, par canal), et veut ajuster les fréquences de 21 C-130J en un seul clic, ou importer le comm plan d'une autre mission via un fichier JSON template.

**Ce que l'outil fait :**
- Parse le fichier `mission` (Lua) contenu dans le `.miz`
- Extrait tous les slots Client avec leurs radios et canaux
- Présente une interface d'édition groupée par type d'appareil
- Applique les modifications par patch chirurgical (sans réécrire le fichier)
- Reconstruit le `.miz` et déclenche le téléchargement

**Ce que l'outil ne fait pas :**
- Éditer les slots Player, IA ou autres skills
- Éditer les unités au sol, les missions d'IA, les zones de déclenchement
- Modifier la modulation (conservée à la sauvegarde, non éditable en UI)
- Modifier les `channelsNames` (conservés tels quels)
- Valider les plages de fréquences par rapport aux spécifications radio

**Fichier livrable :** `dcs_comm_plan_editor_v1_0_0.html`

---

## 2. Démarrage rapide

### Charger une mission

Au démarrage, l'outil affiche une **drop-zone plein écran** avec l'icône 📡. Glisser-déposer un `.miz` sur la zone, cliquer sur la drop-box ou cliquer sur le bouton "📂 Choisir un fichier .miz". Le fichier reste strictement local — aucun contenu n'est envoyé à un serveur.

Après chargement (~1 à 3 secondes selon la taille du `.miz`) :
- La drop-zone disparaît, l'UI principale apparaît
- Le nom du fichier s'affiche en haut à droite du header en ambre
- Les cartes par type d'appareil s'affichent dans la grille principale
- Les filtres et le footer deviennent actifs

Pour charger un autre `.miz` sans recharger la page : utiliser le bouton **"📂 Charger un autre .miz"** dans le footer (à gauche des boutons de template). Si des modifications sont en attente, une confirmation est demandée avant de réinitialiser.

### Naviguer et filtrer

- **Recherche libre** : filtre simultanément les cartes et la boîte à cocher par type d'appareil ou callsign
- **Coalition** / **Catégorie** : filtres dropdown
- **Modifié seulement** : n'afficher que les types comportant au moins une modification en attente
- **Afficher/masquer les types** : sélecteur à cocher trié alphabétiquement, permet d'isoler un sous-ensemble de types

### Éditer une fréquence

Cliquer sur la valeur numérique d'un canal pour l'éditer. La cellule passe en mode édition (bordure ambre, texte phosphore). Quitter le champ (Tab ou clic ailleurs) valide la modification. Un bouton `↶` apparaît à droite de la cellule pour annuler cette modification individuelle.

Pour les types avec plusieurs slots identiques (ex. C-130J ×21), modifier la fiche unique applique la modification aux 21 slots simultanément. Le compteur en bas à gauche l'indique.

Pour les types avec des configurations divergentes (ex. F-15ESE ×2 avec des canaux différents), un bouton **Casser en variantes** permet d'éditer chaque slot indépendamment.

### Sauvegarder

Le bouton **💾 Sauvegarder** (en bas à droite) devient actif dès qu'au moins une modification est en attente. Un clic génère un nouveau `.miz` nommé `{nom_original}_radios_{YYYYMMDD-HHMM}.miz` et déclenche le téléchargement. L'UI reste active avec les valeurs mises à jour — il est possible de continuer à travailler et sauvegarder à nouveau sans recharger la page.

### Templates JSON

**Exporter :** le bouton **📤 Exporter template** génère un fichier JSON `{nom}.._radios_template_{YYYYMMDD-HHMM}.json` contenant la configuration radio courante de tous les types avec radio.

**Importer :** le bouton **📥 Importer template** ouvre un sélecteur de fichier. Après sélection d'un template JSON, une modale récapitulative indique combien de modifications ont été générées, quels types ont été ignorés (absents du `.miz`), et si des valeurs invalides ont été écartées.

---

## 3. Architecture

### 3.1 Stack

- **HTML/CSS/JS vanilla** — aucun framework, pas de build pipeline
- **JSZip 3.10.1** — décompression/recompression du `.miz` (embarqué inline)
- **Un seul fichier** — tout le code, la logique et la UI sont dans `dcs_comm_plan_editor_v1_0_0.html`

### 3.2 Couches applicatives

```
Fichier .miz (zip)
    │
    ▼
[DCS_TOKENIZER]        Tokenization du Lua DCS → flux de tokens avec positions sources
    │
    ▼
[DCS_PARSER]           Construction d'un AST récursif (tables, paires clé/valeur)
    │
    ▼
[DCS_EXTRACTOR]        Extraction sémantique → MissionModel
                       (clientGroups, typeConventions, syncPositions, otherFiles)
    │
    ▼
[UI_STATE + typeViews] Consolidation par type d'appareil, détection des divergences
    │
    ▼
[Rendu des cartes]     Grille CSS responsive, inputs actifs, feedback visuel
    │
    ▼
[UI_STATE.edits]       Map des modifications en attente (clé → {oldValue, newValue, sourcePos})
    │
    ▼
[Pipeline save]        A: collecte + filtrage no-op
                       B: couplage canal ↔ group.frequency + tri offset décroissant
                       C: application chirurgicale des patches
                       D: retokenize de sécurité
                       E: reconstruction zip + téléchargement
                       F: ré-extraction du modèle (persistance post-save)
```

### 3.3 MissionModel

La structure extraite par `DCS_EXTRACTOR` :

```javascript
model = {
  clientGroups: [          // Un élément par slot Client
    {
      group: {
        groupId, groupName,
        frequency: {
          value,           // Valeur numérique
          valuePos,        // Position dans le source pour patch
          modulation,
          modulationPos,
        },
      },
      unit: {
        unitId, name, type, callsign,
        radios: [          // Null si RADIO_BLOCK_MISSING
          {
            index,         // 1, 2, 3... (numéro de la radio)
            channels: {    // Clé = numéro de canal
              [N]: { frequency, frequencyPos }
            },
            modulations,   // Null si pas de bloc modulations dans le Lua
          }
        ],
        syncPositions: [   // Canaux détectés comme synchro avec group.frequency
          { radioIndex, channelNumber, modulation }
        ],
      },
      coalition,           // "blue" | "red" | "neutrals"
      category,            // "helicopter" | "plane"
    }
  ],
  typeConventions: {       // Conventions par type d'appareil
    [type]: {
      isUniform,           // true si tous les slots ont les mêmes fréquences
      syncSignature,       // [] si aucun canal sync (no-sync), [radioIdx/chNum, ...] sinon
      variants,            // Sous-groupes si non uniforme
    }
  },
  source: {
    _text,                 // Texte brut du fichier mission (pour patch)
    miz: {
      filename,
      _otherFilesData,     // Map nom → Uint8Array (tous les fichiers hors mission)
    },
  },
}
```

### 3.4 Pattern de chargement Mission Suite

Au démarrage, seule `#drop-zone` est visible (les autres sections ont la classe `.hidden`). Après chargement réussi :

```javascript
document.getElementById('drop-zone').classList.add('hidden');
document.getElementById('filters').classList.remove('hidden');
document.getElementById('type-selector').classList.remove('hidden');
document.getElementById('cards-container').classList.remove('hidden');
document.getElementById('modifications-bar').classList.remove('hidden');
```

Ce pattern est identique au Ground Unit Swapper. Toute évolution qui modifierait le flow de chargement doit conserver cette symétrie Mission Suite.

Le bouton `.btn-load-new` dans le footer effectue l'opération inverse : remet `.hidden` sur les 4 sections UI, retire `.hidden` sur `#drop-zone`, et réinitialise `UI_STATE` (modèle, edits, filtres). Si des edits sont en attente, un `confirm()` natif est présenté.

---

## 4. Format `.miz` DCS

### 4.1 Structure du zip

Un fichier `.miz` est un zip standard contenant au minimum :

| Fichier | Contenu |
|---|---|
| `mission` | Le fichier principal — Lua sérialisé par ED, UTF-8 |
| `options` | Options de la mission |
| `theatre` | Nom du théâtre (Caucasus, Syria, etc.) |
| `warehouses` | Données des dépôts de munitions/carburant |
| `l10n/DEFAULT/dictionary` | Dictionnaire de localisation |
| `l10n/DEFAULT/mapResource` | Ressources cartographiques |
| `KNEEBOARD/` | Dossiers de kneeboard par pays/coalition |

L'outil lit uniquement le fichier `mission`. Tous les autres fichiers (`otherFiles`) sont conservés intacts dans le zip reconstruit.

### 4.2 Structure du fichier `mission` (Lua)

Le fichier `mission` est du Lua sérialisé par ED — une table Lua racine avec des sous-tables imbriquées. L'outil traite uniquement la hiérarchie suivante :

```
mission
  coalition
    [coalitionName]          -- "blue" | "red" | "neutrals"
      country
        [N]
          helicopter | plane
            group
              [G]
                frequency    -- group.frequency (MHz)
                modulation   -- 0=AM, 1=FM
                units
                  [U]
                    type     -- "Mi-24P", "F-15ESE", etc.
                    skill    -- "Client" (seul cas traité)
                    Radio
                      [R]    -- index de la radio (1, 2, 3...)
                        channels
                          [C]  -- numéro de canal
                            frequency
```

### 4.3 Variantes de format

La structure ED varie selon les versions du jeu et le type d'appareil :

- Certains appareils n'ont pas de bloc `Radio` (`RADIO_BLOCK_MISSING`) — ce sont les slots "fantômes" affichés comme SANS RADIO dans l'UI.
- Certains appareils n'ont pas de bloc `modulations` dans leur radio (ex. Mi-24P) — la modulation est mono-mode et non configurable dans le `.miz`.
- Les clés de table peuvent être des entiers (`[1]`) ou des chaînes (`["blue"]`) — le parser gère les deux formes.

---

## 5. Détection de synchronisation

### 5.1 Principe

Dans DCS, chaque groupe possède une `group.frequency` qui sert aux communications IA inter-groupes. Pour les appareils équipés de radios configurables, cette valeur est typiquement synchronisée avec l'un des canaux préréglés (souvent le canal 1 de la radio principale).

L'extracteur détecte automatiquement ce couplage par analyse comparative : si `group.frequency` correspond à la fréquence d'un canal donné dans tous les slots d'un type, ce canal est déclaré `syncPosition`.

### 5.2 Types de sync (`typeConventions`)

| Cas | `syncSignature` | Comportement |
|---|---|---|
| Canal sync détecté | `[{radioIndex, channelNumber}]` | Modification du canal → mise à jour auto de `group.frequency` à la sauvegarde |
| Pas de canal sync | `[]` (vide) | Panneau "Fréquence groupe" affiché et éditable indépendamment |
| Slot sans radio | N/A | Carte en lecture seule, aucune édition possible |

### 5.3 Couplage à la sauvegarde

Quand un canal sync est modifié, le pipeline save (étape B) génère automatiquement un patch supplémentaire sur `group.frequency` pour maintenir la cohérence. Ce comportement est conservatif : si `group.frequency` est déjà à la bonne valeur, le patch n'est pas généré (filtrage no-op).

---

## 6. Catalogue radio (`ACFT_RADIO_MAP`)

### 6.1 Rôle

Le tableau `ACFT_RADIO_MAP` (embarqué dans le code) mappe chaque type d'appareil DCS à des noms commerciaux de radios :

```javascript
const ACFT_RADIO_MAP = {
  "Mi-24P": { 1: "R-863 (VHF/UHF)", 2: "R-828 (VHF FM)", 3: "Jadro-1I (HF)" },
  "F-15ESE": { 1: "AN/ARC-164 (UHF - COMM 1)", 2: "AN/ARC-186 (V/UHF - COMM 2)" },
  // ...
};
```

Ces noms apparaissent en en-tête des tableaux de canaux dans chaque carte.

### 6.2 Graceful degradation

Si un type d'appareil est absent de `ACFT_RADIO_MAP`, ou si un index de radio n'y est pas référencé, l'UI affiche simplement `Radio N` sans suffixe. Aucune erreur n'est levée.

### 6.3 Ajouter un type manquant

Ouvrir `dcs_comm_plan_editor_v1_0_0.html` dans un éditeur, rechercher `const ACFT_RADIO_MAP`, et ajouter une entrée :

```javascript
"MonNouvelAppareil": { 1: "Nom commercial radio 1", 2: "Nom commercial radio 2" },
```

La clé doit correspondre exactement à la valeur du champ `type` dans le fichier `mission` DCS (sensible à la casse).

---

## 7. Patch chirurgical

### 7.1 Principe

L'outil ne régénère pas le fichier `mission` — il **réécrit uniquement les valeurs modifiées** dans le texte source original, en conservant le formatage, les commentaires, l'ordre des clés, et les métadonnées ED.

### 7.2 Mécanique

Chaque position lue par le parser est stockée sous la forme `{ start: { offset, line, col }, end: { offset, line, col } }`. À la sauvegarde :

1. **Collecte** : les edits de `UI_STATE.edits` sont convertis en patches `{ pos, newValueStr }`.
2. **Filtrage no-op** : si la valeur dans le source à la position donnée est déjà égale à la nouvelle valeur, le patch est ignoré (comparaison numérique avec tolérance `1e-9`).
3. **Couplage** : les patches sur des canaux sync génèrent des patches additionnels sur `group.frequency` (et éventuellement `group.modulation` si incohérent).
4. **Tri décroissant par offset** : les patches sont appliqués de la fin du fichier vers le début, ce qui garantit que les offsets des patches non encore appliqués restent valides.
5. **Application** : pour chaque patch, `source.substring(0, start.offset) + newValueStr + source.substring(end.offset)`.
6. **Retokenize de sécurité** : le texte patché est retokenizé. En cas d'erreur, une modale bloque le téléchargement et conserve les modifications dans l'UI.

### 7.3 Format des valeurs patchées

Les fréquences sont sérialisées sans zéros traînants inutiles :
- `399.9` → `"399.9"` (pas `"399.900"`)
- `251` → `"251"` (pas `"251.0"` ni `"251.000"`)
- `124.5` → `"124.5"`

Ce format correspond au style ED dans les fichiers `.miz` récents.

---

## 8. Templates JSON

### 8.1 Format

```json
{
  "format": "dcs-comm-plan-template-v1",
  "exportedAt": "2026-05-24T14:32:00.000Z",
  "sourceMiz": "Foothold_SY.miz",
  "configurations": {
    "Mi-24P": {
      "groupFrequency": 399.9,
      "groupModulation": 0,
      "radios": {
        "1": {
          "1": { "frequency": 399.9 },
          "2": { "frequency": 252.1 }
        },
        "2": {
          "1": { "frequency": 30.0 }
        }
      }
    }
  }
}
```

- La clé de premier niveau dans `configurations` est le `type` DCS exact de l'appareil.
- Les types SANS RADIO sont absents de `configurations`.
- Les types non uniformes (variants) sont exportés au slot représentatif — les variantes individuelles ne sont pas préservées dans le format v1.

### 8.2 Workflow export / import

**Export :** snapshot de l'état courant (modèle + edits en cours). Les edits non encore sauvegardés sont inclus dans les valeurs exportées.

**Import :**
- Les types du template absents du `.miz` chargé sont ignorés silencieusement (log console).
- Les types du `.miz` absents du template sont laissés intacts.
- Les fréquences invalides (NaN, négatives, non numériques) sont ignorées avec un avertissement dans la modale récapitulative.
- L'import génère des entrées dans `UI_STATE.edits` — les modifications ne sont pas appliquées au `.miz` tant que l'utilisateur ne clique pas sur Sauvegarder.
- La fréquence groupe (`groupFrequency`) est appliquée uniquement pour les types sans sync (types où le panneau "Fréquence groupe" est visible dans l'UI).

---

## 9. Limitations connues

| Limitation | Détail |
|---|---|
| Modulation non éditable | La colonne modulation est masquée dans l'UI. La valeur est conservée à la sauvegarde. |
| `channelsNames` ignoré | Ce bloc Lua est conservé intact mais l'UI ne l'affiche pas ni ne le modifie. |
| Validation par plages | Aucune vérification que la fréquence saisie est dans la plage valide pour la radio concernée (Phase 1E). |
| Catalogue radio peut dériver | Si ED ajoute un module DCS après la release, son nom de radio apparaîtra comme `Radio N` jusqu'à la prochaine mise à jour de `ACFT_RADIO_MAP`. |
| Templates v1 et variants | Les types non uniformes (ex. F-15ESE avec deux slots aux fréquences différentes) sont exportés au slot représentatif uniquement. Un template importé appliquera la même valeur aux deux slots. |
| Nom de fichier long | Si le nom du `.miz` source est très long, le nom du fichier téléchargé peut dépasser 255 caractères sur certains systèmes. |

---

## 10. Glossaire

**Comm plan** : plan de communication d'une mission — attribution des fréquences radio par rôle (strike, cap, tanker, awacs, ground, etc.).

**Slot Client** : slot jouable dans DCS (`skill = "Client"`). L'outil traite exclusivement ces slots.

**group.frequency** : fréquence de communication IA du groupe. Utilisée par DCS pour les échanges entre groupes IA. Pour les appareils jouables, elle est typiquement synchronisée avec l'un des préréglages canal.

**Sync** : situation où `group.frequency` correspond à la fréquence d'un canal radio préréglé. L'outil détecte ce couplage automatiquement et le maintient à la sauvegarde.

**No-sync** : type d'appareil pour lequel aucun canal préréglé ne correspond à `group.frequency`. Le panneau "Fréquence groupe" est affiché et éditable indépendamment dans l'UI.

**Patch chirurgical** : technique de modification de fichier texte consistant à ne réécrire que les sous-chaînes modifiées, en conservant tout le reste intact. Opposé à une sérialisation complète qui réécrirrait le fichier depuis zéro.

**Retokenize de sécurité** : après application des patches, le texte patché est retokenizé par le même tokenizer Lua que lors du chargement. Si une erreur est détectée, le téléchargement est bloqué et une modale d'erreur est affichée. Cette vérification garantit qu'aucun `.miz` corrompu ne sera livré.

**otherFiles** : tous les fichiers du `.miz` autres que `mission` (options, theatre, warehouses, l10n, KNEEBOARD…). Ils sont chargés en mémoire à l'ouverture du `.miz` et réinjectés tels quels dans le zip reconstruit à la sauvegarde.

**MissionModel** : structure de données interne construite par `DCS_EXTRACTOR` à partir de l'AST. C'est la représentation exploitable par l'UI. Elle est reconstruite après chaque sauvegarde pour maintenir la cohérence des positions sources.

**DCS Mission Suite** : collection d'outils HTML monofichiers pour la préparation de missions DCS World — Briefing Generator, Comm Plan Editor, Ground Unit Swapper. Tous partagent la même palette visuelle (cockpit ambre/phosphore) et le même paradigme de fonctionnement (single-file, offline, patch chirurgical).

**Template v1** : format JSON d'échange de configurations radio entre missions. Identifié par `"format": "dcs-comm-plan-template-v1"`. Contient les fréquences par type d'appareil, par radio, par canal.
