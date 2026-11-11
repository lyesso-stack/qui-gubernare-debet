Qui gubernare debet, « celui qui doit gouverner », est un observatoire citoyen de la dépense publique. Il montre où va chaque euro du budget de l'État, qui en répond, et donne au citoyen la lettre pour demander devis et factures. Le site doit avoir l'autorité d'une institution internationale (sobre, dense, sourcé) sans jamais se faire passer pour l'État.

## Ton et contenu

- Phrases courtes, au présent, voussoiement : « Demandez les pièces », « Vous pouvez copier la lettre ».
- Des faits, pas d'adjectifs. On écrit « 205 contrats n'ont reçu qu'une seule offre », jamais « scandale ».
- Pas de point d'exclamation, pas d'émoji, pas d'humour.
- Majuscule en début de phrase seulement ; les libellés en capitales passent par le style `overline` (CSS), jamais tapés en capitales.
- Chiffres à la française : `89,6 Md€`, `1 148 842 977 €` (espace fine), dates « 6 août 2026 ».
- Chaque chiffre porte sa source juste en dessous, en `caption` : « Source : PLF 2026, projet annuel de performances, p. 72 ».
- Les trois états de la chaîne s'écrivent toujours ainsi : **Traçable**, **Lien rompu**, **Non publié**.
- Chaque page porte « Site citoyen indépendant · sans lien avec l'administration » (Masthead) et la mention obligatoire (Mention).
- Interdits : la Marianne, le bloc « République française », le drapeau tricolore, la police Marianne. Le site observe l'État, il ne l'imite pas.

## Couleurs

- Thème `light` par défaut. Le thème `dark` existe, avec ses propres valeurs.
- Fond `page`, cartes et tableaux sur `paper`, en-têtes de tableau sur `paper-sunk`, filets `line`.
- `navy` est la couleur de l'institution : bandeau supérieur et bandeau de titre (PageHead), rien d'autre. Texte dessus : `on-navy`, `on-navy-muted`.
- `blue` ne sert qu'à l'action : bouton principal, liens (`link`), onglet actif. Texte sur un bouton blue : `on-blue`.
- `gold-mark` et `gold` sont réservés au sceau et à la mention obligatoire. Jamais un bouton doré.
- `ok`, `cut`, `no` ne servent qu'aux états de traçabilité, toujours avec leur mot et leur signe (✓ ✕ ○).
- Graphiques : une seule teinte bleue en 4 paliers, `viz-1` à `viz-4`, du plus petit au plus gros montant. Libellés en `on-viz-hi` sur `viz-3` et `viz-4`, en `on-viz-lo` sur `viz-1` et `viz-2`.
- Focus clavier : `focus-ring` (2 px de fond puis 2 px de blue plein) sur tout élément actif.

## Typographie

- Une seule famille : IBM Plex Sans (Google Fonts), et IBM Plex Mono pour les identifiants. Pas de serif.
- `display` une fois par écran (titre du PageHead). `h1` pour le titre d'une fiche, `h2` pour les sections, `h3` pour les cartes.
- `lead` pour le chapeau, `body` pour le texte, `body-sm` dans les tableaux et cartes.
- `figure` pour les chiffres clés, toujours en `font-variant-numeric: tabular-nums`.
- `code` pour SIRET, numéros de marché et codes CPV.

## Mise en page

- Contenu centré, largeur maximale `page-max` (1200 px), marges latérales `space-6`.
- `space-16` entre deux sections, `space-8` entre un titre et son contenu.
- Des filets, pas des ombres. `shadow-float` seulement pour ce qui flotte (infobulle).
- Angles : `radius-0` pour tableaux, bandeaux, tuiles et barres ; `radius-xs` pour étiquettes et champs ; `radius-sm` pour boutons et cartes.
- Ordre d'une page : Masthead, PageHead, Mention, puis le contenu.

## Iconographie

- Pas de bibliothèque d'icônes. Trois signes typographiques pour les états (✓ ✕ ○), la flèche → pour « voir la suite ».
- Le seul emblème est le sceau (`assets/Logos`) : anneau « QVI GVBERNARE DEBET · MMXXVI · REGISTRE CITOYEN » et une balance. En page, le coller en SVG en ligne avec la classe `qg-seal`.
- Pas de photo, pas d'illustration : les chiffres sont l'image.

## Pour coder une page

- Charger les variables (`tokens.css`) puis `components/bundle.css` : toutes les classes commencent par `qg-`.
- Les composants sont du HTML pur, sans bibliothèque : recopier la structure de leur aperçu.
- Seul le treemap a besoin de code : charger `components/bundle.js` puis appeler `QGD.treemap(élément, [[nom, Md€], …], nomSuivi)`.
