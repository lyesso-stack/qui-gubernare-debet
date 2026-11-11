# Qui gubernare debet

Site citoyen indépendant pour suivre l'argent public, de la mission du budget jusqu'au contrat signé, et savoir qui en décide.

> « La Société a le droit de demander compte à tout Agent public de son administration. »
> Déclaration des droits de l'homme et du citoyen de 1789, article 15.

Ce que fait le site :

- le budget de l'État 2026 par mission, puis par programme et par action (mission Enseignement scolaire) ;
- les contrats publiés de l'Éducation nationale, avec une lettre prête pour demander devis et factures ;
- qui dirige l'État : Président, Gouvernement, hauts fonctionnaires, recteurs, préfets, autorités indépendantes, députés et sénateurs ;
- pour chaque mission, programme et acheteur : les noms et les rôles des décideurs, cliquables ;
- pour chaque personne : fonction, nomination au Journal officiel, salaire fixé par les textes, déclarations à la HATVP, parcours (actes au Journal officiel, études et postes) et une lettre prête pour demander sa lettre de mission.

Ce n'est pas un site officiel. Toutes les données viennent de sources publiques, citées sur la page « Méthode ».

## Construire la page

Il faut Python 3.10 ou plus récent, sans bibliothèque à installer.

1. Télécharger les sources publiques dans des dossiers à part (les adresses sont plus bas) :
   - `dl_an/amo10.zip`, `dl_senat/general.csv`, `dl_hatvp/liste.csv`, `dl_etat/ref.zip` ;
   - `python -I tools/dl_pref.py dl_pref` pour les préfectures ;
   - `python -I tools/dl_annu.py 'search(pivot,"rectorat")' dl_rect/rect.json` pour les rectorats ;
   - `python -I tools/dl_annu.py 'search(nom,"affaires financières") and search(nom,"éducation")' dl_siec/s.json`.
2. `python -I build_people.py .` : l'annuaire du pouvoir (`people.json`, `photos.json`).
3. `python -I tools/dl_photos.py photos.json dl_photos`, puis servir le dossier (`python -m http.server`) et ouvrir `sprite.html#an` et `sprite.html#sen` : chaque page rend la planche de photos et la liste des photos réussies, à enregistrer en `ph-an.jpg` / `sprite-an.json` (et de même pour `sen`).
4. `python -I tools/dl_cv.py people.json dl_cv` puis `python -I tools/wd2.py people.json dl_cv` : les parcours.
5. `python -I build_cv.py` puis `python -I build_qgd.py` : la page finale `qgd.html`.

`dl/qgd_decp_education.json` (contrats de l'Éducation nationale) et `pap_actions.json` (actions du projet annuel de performances) sont fournis : ce sont des extraits déjà nettoyés de données publiques.

## Sources

- Budget : loi n° 2026-103 du 19 février 2026 de finances pour 2026 ; projet annuel de performances 2026 de la mission Enseignement scolaire.
- Contrats : données essentielles de la commande publique (data.economie.gouv.fr, data.gouv.fr).
- Administration : référentiel de l'organisation administrative de l'État (DILA, data.gouv.fr) et API Annuaire de l'administration (api-lannuaire.service-public.fr).
- Députés : https://data.assemblee-nationale.fr/static/openData/repository/17/amo/deputes_actifs_mandats_actifs_organes/AMO10_deputes_actifs_mandats_actifs_organes.json.zip
- Sénateurs : http://data.senat.fr/data/senateurs/ODSEN_GENERAL.csv
- Déclarations : https://www.hatvp.fr/livraison/opendata/liste.csv
- Parcours : JORFSearch (https://jorfsearch.steinertriples.ch), d'après le Journal officiel ; Wikidata.

## Licence

Code sous licence GNU AGPL v3 (fichier `LICENSE`) : chacun peut le reprendre et le modifier, mais toute version mise en ligne doit publier son code sous la même licence. Les données restent soumises à la licence de leur source (Licence Ouverte Etalab pour les données publiques françaises, CC0 pour Wikidata).
