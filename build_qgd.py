import json, re
raw = json.load(open('dl/qgd_decp_education.json', encoding='utf-8'))
acts = json.load(open('pap_actions.json', encoding='utf-8'))

missions = [
 ["Enseignement scolaire",89.621,"Salaires des enseignants, de la maternelle au lycée, public et privé sous contrat"],
 ["Défense",66.4755,"Armées, équipements, opérations"],
 ["Engagements financiers de l'État",60.3412,"Surtout les intérêts de la dette de l'État"],
 ["Recherche et enseignement supérieur",31.6339,"Universités, organismes de recherche, bourses étudiantes"],
 ["Solidarité, insertion et égalité des chances",31.2815,"Prime d'activité, allocation adulte handicapé"],
 ["Sécurités",25.8446,"Police, gendarmerie, sécurité civile, sécurité routière"],
 ["Écologie, développement et mobilité durables",22.7628,"Transports, énergie, climat, prévention des risques"],
 ["Cohésion des territoires",22.5709,"Aides au logement, hébergement d'urgence, politique de la ville"],
 ["Travail et emploi",20.8206,"France Travail, apprentissage, retour à l'emploi"],
 ["Justice",12.9666,"Tribunaux, prisons, protection judiciaire de la jeunesse"],
 ["Gestion des finances publiques",11.0179,"Les agents des impôts et des douanes"],
 ["Régimes sociaux et de retraite",6.0679,"Retraites des régimes spéciaux"],
 ["Administration générale et territoriale de l'État",5.0815,"Préfectures, élections, titres d'identité"],
 ["Investissements d'avenir",4.3978,"Plan France 2030"],
 ["Agriculture, alimentation, forêt et affaires rurales",4.1259,""],
 ["Relations avec les collectivités territoriales",3.959,"Subventions d'investissement aux collectivités"],
 ["Culture",3.7445,""],
 ["Aide publique au développement",3.5694,""],
 ["Économie",3.5126,""],
 ["Action extérieure de l'État",3.4544,"Ambassades, consulats"],
 ["Outre-mer",3.2774,""],
 ["Immigration, asile et intégration",2.1306,""],
 ["Santé",1.8881,"Aide médicale d'État, prévention"],
 ["Anciens combattants, mémoire et liens avec la nation",1.73,""],
 ["Sports, jeunesse et vie associative",1.2589,""],
 ["Pouvoirs publics",1.1402,"Élysée, Assemblée, Sénat, Conseil constitutionnel"],
 ["Direction de l'action du Gouvernement",1.0525,"Services du Premier ministre"],
 ["Conseil et contrôle de l'État",0.8661,"Conseil d'État, Cour des comptes"],
 ["Médias, livre et industries culturelles",0.703,""],
 ["Transformation et fonction publiques",0.5183,""],
 ["Crédits non répartis",0.475,"Réserve pour imprévus"]]
assert len(missions) == 31

meta = {
 '140': ("École publique, maternelle et élémentaire", ["Caroline Pascal", "Directrice générale de l'enseignement scolaire"], 30),
 '141': ("Collèges et lycées publics", ["Caroline Pascal", "Directrice générale de l'enseignement scolaire"], 72),
 '230': ("Vie scolaire, santé scolaire, accompagnement des élèves handicapés, aides sociales", ["Caroline Pascal", "Directrice générale de l'enseignement scolaire"], 140),
 '139': ("Écoles, collèges et lycées privés sous contrat : l'État paie leurs enseignants", ["Marine Camiade", "Directrice des affaires financières"], 186),
 '214': ("Administration centrale, rectorats, informatique, examens, ressources humaines", ["Thierry Le Goff", "Secrétaire général"], 244),
 '143': ("Lycées agricoles, géré par le ministère de l'Agriculture", ["Benoît Bonaimé", "Directeur général de l'enseignement et de la recherche, ministère de l'Agriculture"], 320),
}
progs, cur = [], None
for a in acts:
    if len(a['code']) == 3:
        d, resp, page = meta[a['code']]
        cur = {'code': a['code'], 'label': a['label'], 'desc': d, 'resp': resp, 'page': page, 'cp25': a['cp25'], 'cp26': a['cp26'], 'actions': []}
        progs.append(cur)
    else:
        cur['actions'].append({'code': a['code'], 'label': a['label'], 'cp25': a['cp25'], 'cp26': a['cp26']})
for p in progs:
    assert sum(x['cp26'] for x in p['actions']) == p['cp26'], p['code']
    assert sum(x['cp25'] for x in p['actions']) == p['cp25'], p['code']

buyers = {
 '11004301500012': ["Ministère de l'Éducation nationale, administration centrale", "Paris"],
 '17130430600011': ["Rectorat de l'académie d'Aix-Marseille", ""],
 '17250430000010': ["Rectorat de l'académie de Besançon", ""],
 '17340430200015': ["Rectorat de l'académie de Montpellier", ""],
 '17350430900019': ["Rectorat de l'académie de Rennes", ""],
 '17380430300019': ["Rectorat de l'académie de Grenoble", ""],
 '17440430100015': ["Rectorat de l'académie de Nantes", ""],
 '17450430800019': ["Rectorat de l'académie d'Orléans-Tours", ""],
 '17590431700013': ["Services départementaux de l'Éducation nationale du Nord", ""],
 '17690430800010': ["Rectorat de l'académie de Lyon", ""],
 '17750430500091': ["Service interacadémique des examens et concours (SIEC)", "Arcueil"],
 '17750430500133': ["Rectorat de l'académie de Paris", ""],
 '17780430900199': ["Rectorat de l'académie de Versailles", ""],
 '17940430600088': ["Rectorat de l'académie de Créteil", ""],
}
assert sorted(buyers) == sorted(raw['buyers'])

def lieu(c):
    t, v = c.get('lieuexecution_typecode') or '', c.get('lieuexecution_code') or ''
    if not v: return ''
    return {'Code département': 'Département ', 'Code postal': 'Code postal ', 'Code pays': 'Pays '}.get(t, '') + v

def clean(t):  # la source garde des retours chariot codés (#x0D;) et des "\n" écrits en toutes lettres
    t = re.sub(r'&?#x0D;?|\\[nrt]', ' ', t or '')
    return re.sub(r'\s+', ' ', t).strip()

rows = []
for c in raw['contracts']:
    co = sum(1 for k in ('titulaire_id_2', 'titulaire_id_3') if re.fullmatch(r'\d{9,14}', str(c.get(k) or '')))  # 'CDL' = champ vide
    off = c.get('offresrecues')
    rows.append([c['id'], c['acheteur_id'], clean(c.get('objet')), round(c['montant'] or 0), c['datenotification'], c.get('dureemois'),
                 c['titulaire_id_1'], co, c.get('codecpv') or '', c.get('procedure') or '', str(off) if off not in (None, '') else '', lieu(c),
                 c.get('datepublicationdonnees') or '', c.get('formeprix') or ''])
sup = {}
for c in rows:
    s = c[6][:9]; n = raw['names'].get(s, {})
    sup[s] = [n.get('n'), (n.get('v') or '').title()]
assert len(rows) == 559 and all(r[3] > 0 for r in rows)
assert not any(re.search(r'#x0D|\\[nrt]|\s\s', r[2]) for r in rows)

# Annuaire du pouvoir (build_people.py) et place de chaque photo dans sa planche (sprite.html)
pp = json.load(open('people.json', encoding='utf-8'))
order = {g: [x[1] for x in json.load(open('photos.json')) if x[0] == g] for g in ('an', 'sen')}
for g in order:
    ok = set(json.load(open('sprite-%s.json' % g))['ok'])
    pos = {pid: i for i, pid in enumerate(order[g]) if pid in ok}
    for p in pp['pp']:
        if p['g'] == g and p['id'] in pos:
            p['ph'] = pos[p['id']]

# Salaires officiels. Base : indemnité parlementaire au 1er janvier 2026 (AN, fiche n° 7, janvier 2026).
BASE = 5931.95
dep = [['Indemnité de base', BASE], ['Indemnité de résidence (3 %)', 177.96], ['Indemnité de fonction (25 %)', 1527.48]]
assert round(sum(x[1] for x in dep), 2) == 7637.39


def gov(k, lab):  # loi de finances rectificative pour 2002 puis baisse de 30 % (décret n° 2012-983)
    b = round(2 * BASE * k, 2); r = round(b * .03, 2); f = round((b + r) * .25, 2); cut = -round((b + r + f) * .3, 2)
    rows = [[lab, b], ['Indemnité de résidence (3 %)', r], ['Indemnité de fonction (25 %)', f], ['Baisse de 30 % (décret n° 2012-983 du 23 août 2012)', cut]]
    return rows, round(b + r + f + cut, 2)


mr, mt = gov(1, 'Traitement de base : 2 × 5 931,95 €')
pr_, pt = gov(1.5, 'Traitement de base : 2 × 5 931,95 € × 1,5')
assert int(mt) == 10692 and int(pt) == 16038, (mt, pt)  # montants publiés (euros entiers) : 10 692 € et 16 038 €
sal = {'dep': {'rows': dep, 'tot': 7637.39, 'net': 5953.34}, 'min': {'rows': mr, 'tot': mt}, 'pm': {'rows': pr_, 'tot': pt}}

# Qui décide : chaque mission, programme et acheteur relié aux personnes de l'annuaire, [id, rôle]
PP = pp['pp']


def one(pred, what):
    r = [p for p in PP if pred(p)]
    assert len(r) == 1, (what, [p['n'] for p in r])
    return r[0]


def minister(key):
    return one(lambda p: p.get('rank') in (0, 1) and key in p.get('min', ''), key)


def named(n):
    return one(lambda p: p['n'] == n, n)


# Ministre rattaché à chaque mission : lecture des décrets d'attributions du Gouvernement
MIS = {"Enseignement scolaire": ["Éducation nationale", "Agriculture"], "Défense": ["Armées"], "Engagements financiers de l'État": ["Économie, des Finances"],
       "Recherche et enseignement supérieur": ["Enseignement supérieur"], "Solidarité, insertion et égalité des chances": ["Travail et des Solidarités", "Santé, des Familles"],
       "Sécurités": ["Intérieur"], "Écologie, développement et mobilité durables": ["Transition écologique", "Transports"],
       "Cohésion des territoires": ["Ville et du Logement", "Aménagement du Territoire"], "Travail et emploi": ["Travail et des Solidarités"], "Justice": ["Justice"],
       "Gestion des finances publiques": ["Action et des Comptes publics"], "Régimes sociaux et de retraite": ["Action et des Comptes publics"],
       "Administration générale et territoriale de l'État": ["Intérieur"], "Investissements d'avenir": ["Premier ministre"],
       "Agriculture, alimentation, forêt et affaires rurales": ["Agriculture"], "Relations avec les collectivités territoriales": ["Aménagement du Territoire"],
       "Culture": ["Culture"], "Aide publique au développement": ["Europe et des Affaires étrangères"], "Économie": ["Économie, des Finances"],
       "Action extérieure de l'État": ["Europe et des Affaires étrangères"], "Outre-mer": ["Outre-mer"], "Immigration, asile et intégration": ["Intérieur"],
       "Santé": ["Santé, des Familles"], "Anciens combattants, mémoire et liens avec la nation": ["Armées"], "Sports, jeunesse et vie associative": ["Sports"],
       "Pouvoirs publics": [], "Direction de l'action du Gouvernement": ["Premier ministre"], "Conseil et contrôle de l'État": [],
       "Médias, livre et industries culturelles": ["Culture"], "Transformation et fonction publiques": ["Action et des Comptes publics"], "Crédits non répartis": ["Action et des Comptes publics"]}
assert sorted(MIS) == sorted(m[0] for m in missions)
dec = {'mis': {k: [[minister(x)['id'], 'Premier ministre' if x == 'Premier ministre' else 'Ministre responsable'] for x in v] for k, v in MIS.items()}}
EDU, AGRI = minister('Éducation nationale'), minister('Agriculture')
# Programme : la personne qui occupe aujourd'hui le poste désigné par le projet annuel de performances
POST = {'140': 'Caroline Pascal', '141': 'Caroline Pascal', '230': 'Caroline Pascal', '139': 'Marine Camiade', '214': 'Mélanie Joder', '143': 'Maud Faipoux'}
dec['prog'] = {}
for p in progs:
    h = named(POST[p['code']])
    row = [[h['id'], 'Responsable du programme · ' + h['f'].split(',')[0] + ', ' + h['o'].split(' - ')[0]]]
    if h['n'] != p['resp'][0]:  # le projet annuel (octobre 2025) nommait quelqu'un d'autre
        was = [x for x in PP if x['n'] == p['resp'][0]]
        row[0].append([was[0]['id'] if was else '', p['resp'][0]])
    row.append([(AGRI if p['code'] == '143' else EDU)['id'], 'Ministre responsable'])
    dec['prog'][p['code']] = row
# Acheteur : la personne qui dirige le service acheteur
BUY = {'11004301500012': [('Mélanie Joder', "Secrétaire générale du ministère : dirige l'administration centrale"), ('Marine Camiade', 'Directrice des affaires financières du ministère')],
       '17750430500133': [('Julie Benetti', "Rectrice de la région académique Île-de-France, rectrice de l'académie de Paris")],
       '17590431700013': [('Sophie Béjean', "Rectrice de l'académie de Lille, dont relèvent les services de l'Éducation nationale du Nord")]}
dec['buy'] = {}
for s in buyers:
    if s in BUY:
        r = [[named(n)['id'], role] for n, role in BUY[s]]
    else:
        h = [p for p in PP if s in p.get('si', []) and re.match('(Vice-)?Rect', p['f'])]
        r = [[x['id'], x['f'] + ' · ' + x['o'].split(' - ')[-1]] for x in h]
    r.append([EDU['id'], 'Ministre responsable'])
    dec['buy'][s] = r
nodir = [s for s in buyers if len(dec['buy'][s]) == 1]
assert nodir == ['17750430500091'], nodir  # seul le SIEC n'a pas de direction publiée dans l'annuaire
cv = json.load(open('cv.json', encoding='utf-8'))
assert all(k in {p['id'] for p in PP} for k in cv)

D = {'missions': missions, 'progs': progs, 'buyers': buyers, 'sup': sup, 'c': rows, 'meta': {'decp': '4 novembre 2026'}, 'pp': pp, 'sal': sal, 'dec': dec, 'cv': cv}
s = json.dumps(D, ensure_ascii=False, separators=(',', ':')).replace('</', '<\/')
html = open('qgd-src.html', encoding='utf-8').read()
assert html.count('/*@DATA@*/null') == 1
ds = 'qgd-ds/project/'
css = open(ds + 'components/bundle.css', encoding='utf-8').read()
assert css.startswith('@import')
css = css.split(chr(10), 1)[1]  # les polices sont chargées par <link> dans la page
for k, v in (('/*@TOKENS@*/', open(ds + 'tokens.css', encoding='utf-8').read()), ('/*@BUNDLE_CSS@*/', css), ('/*@BUNDLE_JS@*/', open(ds + 'components/bundle.js', encoding='utf-8').read())):
    assert html.count(k) == 1, k
    html = html.replace(k, v)
open('qgd.html', 'w', encoding='utf-8').write(html.replace('/*@DATA@*/null', s))
print('ok', len(rows), len(sup), round(sum(r[3] for r in rows)), len(s))
