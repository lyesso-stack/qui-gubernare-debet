import json, os, sys, re
# usage (depuis le dossier de travail) : python -I build_cv.py -> cv.json
# Parcours de chaque personne : mentions au Journal officiel (JORFSearch) et fiche Wikidata.
pp = [p for p in json.load(open('people.json', encoding='utf-8'))['pp'] if p['g'] != 'vac']
KEEP = {'nomination': 'Nomination', 'cessation de fonction': 'Fin de fonction', 'élection': 'Élection', 'promotion': 'Promotion',
        'admission': 'Admission', 'affectation': 'Affectation', 'détachement': 'Détachement', 'intégration': 'Intégration',
        'réintégration': 'Réintégration', 'titularisation': 'Titularisation', 'renouvellement': 'Renouvellement', 'reconduction': 'Reconduction',
        'décoration': 'Décoration', 'élévation': 'Élévation', 'conférés': 'Distinction', 'diplome': 'Diplôme', 'mise à disposition': 'Mise à disposition'}
OTHER_JOB = ('notaire', 'huissier', 'commissaire_de_justice', 'avocat_aux_conseils', 'autorisation_exercice_medecin')


def detail(x):
    t = []
    if x.get('legion_honneur'): t.append("Légion d'honneur" + (', ' + x['grade'].lower() if x.get('grade') else ''))
    if x.get('ordre_merite'): t.append('Ordre national du Mérite' + (', ' + x['grade'].lower() if x.get('grade') else ''))
    if x.get('medaille_militaire'): t.append('Médaille militaire')
    if x.get('medaille_securite_interieure'): t.append('Médaille de la sécurité intérieure')
    for k in ('ministre', 'secretaire_etat'):
        if isinstance(x.get(k), str) and x[k] != 'true': t.append(x[k])
    if x.get('membre_gouvernement') and not t: t.append('Membre du Gouvernement')
    if x.get('cabinet'): t.append('Cabinet : ' + x['cabinet'] + (' · ' + x['grade'].lower() if x.get('grade') and not x.get('legion_honneur') else ''))
    if x.get('prefet_departement'): t.append(('Préfète' if x.get('sexe') == 'F' else 'Préfet') + ' : ' + x['prefet_departement'])
    elif x.get('prefet'): t.append('Corps préfectoral')
    if x.get('sous-prefet_sous-prefecture'): t.append('Sous-préfecture de ' + x['sous-prefet_sous-prefecture'])
    if x.get('secretaire_general_de_prefecture'): t.append('Secrétariat général de préfecture')
    if x.get('recteur_academie'): t.append('Académie de ' + x['recteur_academie'])
    if x.get('ambassadeur_pays'): t.append('Ambassade : ' + x['ambassadeur_pays'])
    if x.get('consul'): t.append('Consulat : ' + x['consul'])
    if x.get('inspecteur_general'): t.append('Inspection générale : ' + x['inspecteur_general'])
    if x.get('cour_comptes'): t.append('Cour des comptes')
    if x.get('cour_cassation'): t.append('Cour de cassation')
    if x.get('cour_appel'): t.append("Cour d'appel de " + x['cour_appel'])
    if x.get('eleve_ena'): t.append("École nationale d'administration, promotion " + x['eleve_ena'] if x['eleve_ena'] != 'true' else "École nationale d'administration")
    if x.get('eleve_polytechnique'): t.append('École polytechnique')
    if x.get('eleve_ens'): t.append('École normale supérieure' + (' ' + x['eleve_ens'] if x['eleve_ens'] != 'true' else ''))
    if x.get('eleve_ira'): t.append("Institut régional d'administration" + (' de ' + x['eleve_ira'] if x['eleve_ira'] != 'true' else ''))
    if x.get('corps'): t.append('Corps : ' + x['corps'])
    if x.get('conseil_administration'): t.append("Conseil d'administration")
    org = [o['nom'] for o in x.get('organisations') or [] if o.get('nom') and o['nom'] != 'Etat au titre']
    if org: t.append(', '.join(org))
    if x.get('grade') and not (x.get('legion_honneur') or x.get('ordre_merite') or x.get('cabinet')): t.append(x['grade'])
    if x.get('parlement') in ('Assemblée nationale', 'Sénat') and x.get('type_ordre') == 'élection': t.append(x['parlement'])
    s = ' · '.join(dict.fromkeys(t))
    return s[:170] + ('…' if len(s) > 170 else '')


cv, stats = {}, [0, 0, 0]
for p in pp:
    f = 'dl_cv/jorf/' + p['id'] + '.json'
    try:
        rows = json.load(open(f, encoding='utf-8'))
    except Exception:
        stats[2] += 1
        continue
    sx = {'Mme': 'F', 'M.': 'M', 'M': 'M'}.get(p.get('civ'))
    keep = []
    for x in rows:
        if x.get('type_ordre') not in KEEP or any(x.get(k) for k in OTHER_JOB):
            continue
        if sx and x.get('sexe') and x['sexe'] != sx:  # homonyme de l'autre sexe
            continue
        if x.get('commission_parlementaire') or x.get('delegation_parlementaire') or x.get('parlement') == 'Commission mixte paritaire':
            continue
        d = detail(x)
        if not d:
            continue
        keep.append([x.get('source_date') or '', KEEP[x['type_ordre']], d, (x.get('source_id') or '').replace('JORFTEXT', '')])
    keep.sort(key=lambda r: r[0], reverse=True)
    if keep:
        cv[p['id']] = {'j': keep[:30], 'n': len(keep)}
        stats[0] += 1
    else:
        stats[1] += 1

# Wikidata : fiche choisie seulement si elle est sûre (identifiant parlementaire, ou homonyme unique et décrit comme acteur public)
if os.path.exists('dl_cv/wd_info.json'):
    W = json.load(open('dl_cv/wd_info.json', encoding='utf-8'))
    for pid, w in W.items():
        closed = {(r[0], r[1]) for r in w[4] if r[2]}
        w[4] = [r for r in w[4] if r[2] or (r[0], r[1]) not in closed]  # même poste en double, avec et sans date de fin
        cv.setdefault(pid, {})['w'] = w
json.dump(cv, open('cv.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('avec parcours', stats[0], 'sans mention retenue', stats[1], 'fichier illisible', stats[2], 'wikidata', sum(1 for v in cv.values() if 'w' in v), 'taille', os.path.getsize('cv.json'))
