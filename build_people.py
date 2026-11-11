"""Assemble l'annuaire du pouvoir : exécutif, administration, Parlement. Sorties : people.json et photos.json (liste à télécharger)."""
import sys, zipfile, json, csv, io, re, unicodedata, collections
S = sys.argv[1]


def txt(v):  # l'AN code les champs vides en {'@xsi:nil': 'true'}
    return v if isinstance(v, str) else ''


def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z]+', ' ', s).strip()


PART = {'de', 'du', 'des', 'la', 'le', "d"}


def nice(nom):  # « DE LA RAUDIÈRE » -> « de La Raudière », « LE GOFF » -> « Le Goff »
    out = []
    for i, w in enumerate(re.split(r'(\s+|-)', nom.strip())):
        if not w.strip() or w == '-':
            out.append(w); continue
        lw = w.lower()
        out.append(lw if (lw in ('de', 'du', 'des', "d'") and i > 0) else lw[:1].upper() + lw[1:])
    s = ''.join(out)
    return re.sub(r"\bD'(\w)", lambda m: "d'" + m.group(1).upper(), s)


def name_of(p):
    return (p.get('prenom', '') + ' ' + nice(p.get('nom', ''))).strip()


# ---------- HATVP ----------
H = collections.defaultdict(list)
for r in csv.DictReader(open(S + '/dl_hatvp/liste.csv', encoding='utf-8'), delimiter=';'):
    H[norm(r['prenom'] + ' ' + r['nom'])].append(r)


def hatvp(prenom, nom, types):
    rows = H.get(norm(prenom + ' ' + nom), [])
    good = [r for r in rows if r['type_mandat'] in types] or ([] if types else rows)
    if not good:
        return None
    pub = [r for r in good if r['statut_publication'] == 'Livrée']
    last = max((r['date_publication'] for r in pub if r['date_publication']), default='')
    return ['https://www.hatvp.fr' + good[0]['url_dossier'], len(pub), last]


people = []


def add(**k):
    people.append(k)
    return k


# ---------- Référentiel de l'organisation administrative de l'État (DILA) ----------
z = zipfile.ZipFile(S + '/dl_etat/ref.zip')
REFNAME = z.namelist()[0]
svc = json.loads(z.read(REFNAME))['service']
by = {s['id']: s for s in svc}
kids = collections.defaultdict(list)
for s in svc:
    for h in s['hierarchie']:
        if h['type_hierarchie'] == 'Service Fils' and h['service'] in by:
            kids[s['id']].append(h['service'])


def named(s):
    return [a for a in s['affectation_personne'] if a['personne'].get('nom')]


def jo(a):
    t = a['personne'].get('texte_reference') or []
    return [t[0]['libelle'], t[0]['valeur']] if t else None


def contact(s):
    m = [x['valeur'] if isinstance(x, dict) else x for x in s.get('adresse_courriel') or []]
    f = s.get('formulaire_contact') or []
    return {'mail': m[0] if m else '', 'form': f[0] if f else '', 'web': (s.get('site_internet') or [{}])[0].get('valeur', '') if s.get('site_internet') else ''}


nid = [0]


def ref_person(s, a, g, par, sal, org=None):
    nid[0] += 1
    p = a['personne']
    return add(id='r%d' % nid[0], n=name_of(p), civ=p.get('civilite', ''), f=a['fonction'], o=org or s['nom'], g=g, par=par, sal=sal,
               jo=jo(a), grade=p.get('grade', ''), sp=s.get('url_service_public', ''), ct=contact(s),
               ht=hatvp(p.get('prenom', ''), p.get('nom', ''), ('gouvernement', 'president', 'autre') if g in ('gouv', 'pr') else ()))


def find(name, under=None):
    pool = [by[k] for k in kids[under]] if under else svc
    return next(s for s in pool if s['nom'] == name)


top = find('Administration centrale')
groups = {by[k]['nom']: k for k in kids[top['id']]}

# Président et son cabinet
ely = find('Présidence de la République', groups['Institutions et juridictions'])
PR = ref_person(ely, named(ely)[0], 'pr', None, 'pr')
for k in kids[ely['id']]:
    s = by[k]
    if s['nom'].startswith('Cabinet'):
        for a in named(s)[:3]:
            ref_person(s, a, 'adm', PR['id'], 'adm', 'Présidence de la République · ' + s['nom'])

# Gouvernement
gov = by[groups['Gouvernement (Premier ministre et ministères)']]
mins = []
for k in kids[gov['id']]:
    m = by[k]
    hd = named(m)
    if not hd:
        continue
    is_pm = m['nom'] == 'Premier ministre'
    M = ref_person(m, hd[0], 'gouv', PR['id'], 'pm' if is_pm else 'min')
    M['min'] = m['nom']; M['rank'] = 0 if is_pm else 1
    if not is_pm:
        M['f'] = hd[0]['fonction'] + ' ' + m['nom'].replace('Ministère ', '', 1)  # « Ministre » + « de l'Intérieur »
    mins.append(M)
    for k2 in kids[m['id']]:
        s = by[k2]
        hs = named(s)
        if not hs:
            if s['nom'].lower().startswith('ministre'):  # poste de ministre sans titulaire dans l'annuaire officiel
                nid[0] += 1
                add(id='r%d' % nid[0], n='Poste sans titulaire', f=s['nom'], o=m['nom'], g='vac', par=M['id'], sp=s.get('url_service_public', ''),
                    note='ruralite' if 'ruralité' in s['nom'] else '')
            continue
        if s['nom'].lower().startswith('ministre') or hs[0]['fonction'].lower().startswith('ministre'):
            nm = name_of(hs[0]['personne'])
            twin = next((p for p in people if p['g'] == 'gouv' and p['n'] == nm), None)
            if twin:  # même personne rattachée à deux ministres (ex. porte-parole et Énergie)
                twin['f2'] = s['nom'] if s['nom'].lower().startswith('ministre') else hs[0]['fonction']
                continue
            D = ref_person(s, hs[0], 'gouv', M['id'], 'min')
            D['f'] = s['nom'] if s['nom'].lower().startswith('ministre') else hs[0]['fonction']; D['o'] = m['nom']; D['rank'] = 2
        else:
            pol = s['type_organisme'] == 'Cabinet ministériel'
            for a in hs[:1]:
                X = ref_person(s, a, 'adm', M['id'], 'cab' if pol else 'adm')
                X['o'] = s['nom']; X['min'] = m['nom']
PM = next(m for m in mins if m['rank'] == 0)
for m in mins:
    if m['rank'] == 1:
        m['par'] = PM['id']
PM['par'] = PR['id']

# Autorités indépendantes et institutions (le chef seulement)
for gname, g in (('Autorités indépendantes', 'aai'), ('Institutions et juridictions', 'inst')):
    for k in kids[groups[gname]]:
        s = by[k]
        if s['nom'] == 'Présidence de la République':
            continue
        hs = named(s)
        if hs:
            ref_person(s, hs[0], g, None, g)

# ---------- Préfets (annuaire local de service-public.fr, API officielle) ----------
INT = next(m for m in mins if m.get('min') == "Ministère de l'Intérieur")


def js(v):  # l'API renvoie les listes sous forme de texte JSON
    return json.loads(v) if isinstance(v, str) and v[:1] in '[{' else (v or [])


prefs = [r for r in json.load(open(S + '/dl_pref/prefectures.json', encoding='utf-8'))
         if any(t['type_service_local'] in ('prefecture', 'prefecture_region') for t in js(r['pivot']))]
REG = {}
for r in prefs:  # libellé lisible de chaque région, depuis les préfectures de région
    if r['nom'].startswith('Préfecture de région - '):
        lab = r['nom'].split(' - ', 1)[1]
        REG[re.sub(r'[^a-z]+', '-', norm(lab)).strip('-')] = lab
byname = {}
for r in sorted(prefs, key=lambda r: r['nom'].startswith('Préfecture de région')):  # départements d'abord
    region_post = r['nom'].startswith('Préfecture de région')
    slug = (r.get('url_service_public') or '').split('/')[3:4]
    region = REG.get(slug[0], 'Île-de-France' if slug == ['ile-de-france'] else 'Outre-mer') if slug else ''
    terr = r['nom'].split(' - ', 1)[1] if ' - ' in r['nom'] else r['nom']
    hs = [a for a in js(r['affectation_personne']) if a['personne'].get('nom')]
    hs = [a for a in hs if re.search(r"préf|haut-commissaire|représentant de l'état", a['fonction'], re.I)]
    ct = {'mail': (r.get('adresse_courriel') or '').split(';')[0].strip(), 'form': (js(r.get('formulaire_contact')) or [''])[0],
          'web': ((js(r.get('site_internet')) or [{}])[0] or {}).get('valeur', '')}
    if not hs:
        if not region_post and terr.split(' (')[0] and r['nom'].startswith('Préfecture'):
            nid[0] += 1
            add(id='r%d' % nid[0], n='Poste sans titulaire', f='Préfet ou préfète · ' + terr, o=r['nom'], g='vac', vt='pref', reg=region, dep=terr,
                sp=r.get('url_service_public', ''), note='prefet')
        continue
    a = hs[0]; p = a['personne']; nm = name_of(p)
    f = a['fonction']
    if f in ('Préfet', 'Préfète'):  # le genre suit la civilité (une fiche source dit « Préfète » pour un homme)
        f = 'Préfète' if p.get('civilite') == 'Mme' else 'Préfet'
    if f in ('Préfet', 'Préfète', 'Préfet de région', 'Préfète de région'):
        f = f.split(' de région')[0] + (' de la région ' + terr if region_post else ' · ' + terr)
    if terr.startswith('Annexe de '):  # Saint-Barthélemy et Saint-Martin partagent un préfet
        f = 'Préfet de Saint-Barthélemy et de Saint-Martin'
    if nm in byname:  # même personne : préfet de région et du département chef-lieu, ou de deux territoires
        tw = byname[nm]
        if region_post and 'région' not in tw['f'].lower():  # un seul intitulé court : région · département
            tw['f'] = ('Préfète' if tw.get('civ') == 'Mme' else 'Préfet') + ' de la région ' + terr + ' · ' + tw['dep']
        elif not region_post and f != tw['f']:
            tw['f2'] = (tw.get('f2', '') + ' ; ' if tw.get('f2') else '') + f
        continue
    nid[0] += 1
    byname[nm] = add(id='r%d' % nid[0], n=nm, civ=p.get('civilite', ''), f=f, o=r['nom'], g='pref', par=INT['id'], sal='adm',
                     jo=jo(a), grade=p.get('grade', ''), sp=r.get('url_service_public', ''), ct=ct, reg=region, dep=terr,
                     ht=hatvp(p.get('prenom', ''), p.get('nom', ''), ()))

# ---------- Recteurs et direction financière de l'Éducation nationale : ceux qui dirigent les acheteurs des contrats ----------
EDU = next(m for m in mins if m.get('min') == "Ministère de l'Éducation nationale")
rect = json.load(open(S + '/dl_rect/rect.json', encoding='utf-8')) + [r for r in json.load(open(S + '/dl_siec/s.json', encoding='utf-8')) if r['nom'].startswith('Direction des affaires financières')]
seen = {p['n']: p for p in people if p['g'] == 'adm'}
for r in sorted(rect, key=lambda r: r['nom']):
    for a in js(r['affectation_personne']):
        if not a['personne'].get('nom') or not re.match(r'(Vice-)?[Rr]ect|Direct(rice|eur)$', a['fonction']):
            continue
        p = a['personne']; nm = name_of(p)
        if nm in seen:  # recteur de région académique et d'académie : une seule fiche
            x = seen[nm]
            if r.get('siret') and r['siret'] not in x.setdefault('si', []):
                x['si'].append(r['siret'])
            continue
        nid[0] += 1
        seen[nm] = add(id='r%d' % nid[0], n=nm, civ=p.get('civilite', ''), f=a['fonction'], o=r['nom'], g='adm', par=EDU['id'], sal='adm',
                       jo=jo(a), grade=p.get('grade', ''), sp=r.get('url_service_public', ''), si=[r['siret']] if r.get('siret') else [],
                       ct={'mail': (r.get('adresse_courriel') or '').split(';')[0].strip(), 'form': (js(r.get('formulaire_contact')) or [''])[0]},
                       ht=hatvp(p.get('prenom', ''), p.get('nom', ''), ()))
        break  # le premier titre de chaque fiche : le recteur, pas ses adjoints

# ---------- Assemblée nationale ----------
za = zipfile.ZipFile(S + '/dl_an/amo10.zip')
org = {}
for n in za.namelist():
    if '/organe/' in n:
        o = json.loads(za.read(n))['organe']
        org[o['uid']] = o
photos = []
SPEC = {'Président': 7698.50, 'Présidente': 7698.50, 'Questeur': 5300.36, 'Questeure': 5300.36, 'Vice-président': 1099.79, 'Vice-présidente': 1099.79, 'Secrétaire': 733.19}
qual = collections.Counter()
for n in sorted(za.namelist()):
    if '/acteur/' not in n:
        continue
    a = json.loads(za.read(n))['acteur']
    uid = a['uid']['#text'] if isinstance(a['uid'], dict) else a['uid']
    ec = a['etatCivil']['ident']
    ms = a['mandats']['mandat']
    ms = ms if isinstance(ms, list) else [ms]
    act = [m for m in ms if not m.get('dateFin')]
    seat = next((m for m in act if m['typeOrgane'] == 'ASSEMBLEE'), None)
    if not seat:
        continue
    gp = next((org[m['organes']['organeRef']] for m in act if m['typeOrgane'] == 'GP'), None)
    roles, spec = [], 0
    for m in act:
        q = m['infosQualite']['libQualiteSex'] or m['infosQualite']['libQualite']
        if m['typeOrgane'] == 'BUREAU':
            qual[q] += 1
            if "d'âge" in q:  # rôle d'une seule séance, sans indemnité spéciale
                continue
            roles.append(q); spec = max(spec, next((v for k, v in SPEC.items() if q.startswith(k + ' ')), 0))
        if m['typeOrgane'] == 'COMPER' and m['infosQualite']['codeQualite'] in ('Président', 'Présidente'):
            roles.append(q + ' de la ' + org[m['organes']['organeRef']]['libelle'].lower()); spec = max(spec, 931.76)
    lieu = seat['election']['lieu']
    num = txt(lieu['numCirco'])
    lieu = {k: txt(v) for k, v in lieu.items()}
    circ = (lieu['departement'] or lieu.get('region') or '') + ', ' + num + ('re' if num == '1' else 'e') + ' circonscription'
    prof = txt((a.get('profession') or {}).get('libelleCourant'))
    prof = re.sub(r'^\(\d+\)\s*-\s*', '', prof)
    pnum = uid[2:]
    photos.append(['an', uid, 'https://www.assemblee-nationale.fr/dyn/static/tribun/17/photos/carre/%s.jpg' % pnum])
    add(id=uid, n=(ec['prenom'] + ' ' + ec['nom']).strip(), civ=ec['civ'], f=('Député' if ec['civ'] == 'M.' else 'Députée') + ' · ' + circ,
        o='Assemblée nationale', g='an', par=None, sal='dep', spec=spec, roles=roles, since=txt(seat.get('dateDebut')),
        grp=[gp['libelleAbrege'], gp['libelle']] if gp else ['NI', 'Non inscrit'], dep=lieu['departement'] or lieu.get('region') or '',
        prof=prof, page='https://www.assemblee-nationale.fr/dyn/deputes/' + uid, ht=hatvp(ec['prenom'], ec['nom'], ('depute',)))

# ---------- Sénat ----------
raw = open(S + '/dl_senat/general.csv', 'rb').read().decode('cp1252')
rows = list(csv.DictReader(io.StringIO('\n'.join(l for l in raw.splitlines() if not l.startswith('%')))))
GS = {'Les Républicains': 'Les Républicains', 'UCI': 'Union centriste', 'SER': 'Socialiste, écologiste et républicain', 'CRCE-K': 'Communiste républicain citoyen et écologiste – Kanaky',
      'RDSE': 'Rassemblement démocratique et social européen', 'RDPI': 'Rassemblement des démocrates, progressistes et indépendants', 'GEST': 'Écologiste – Solidarité et territoires',
      'UNT': 'Union des non-inscrits et des territoires', 'Les Indépendants': 'Les Indépendants – République et territoires', 'NI': 'Non inscrits'}
for r in rows:
    if r['État'] != 'ACTIF':
        continue
    slug = re.sub(r'[^a-z0-9]+', '_', norm(r['Nom usuel'] + ' ' + r['Prénom usuel'])) + r['Matricule'].lower()
    sid = 'S' + r['Matricule']
    photos.append(['sen', sid, 'http://www.senat.fr/senimg/%s_carre.jpg' % slug])
    roles = [r['Fonction au Bureau du Sénat']] if r['Fonction au Bureau du Sénat'] else []
    fem = r['Qualité'] == 'Mme'
    add(id=sid, n=r['Prénom usuel'] + ' ' + r['Nom usuel'], civ=r['Qualité'], f=('Sénatrice' if fem else 'Sénateur') + ' · ' + r['Circonscription'],
        o='Sénat', g='sen', par=None, sal='sen', roles=roles, grp=[r['Groupe politique'], GS.get(r['Groupe politique'], r['Groupe politique'])],
        dep=r['Circonscription'], com=r['Commission permanente'], prof=r['Description de la profession'],
        page='https://www.senat.fr/senateur/%s.html' % slug, ht=hatvp(r['Prénom usuel'], r['Nom usuel'], ('senateur',)))

# ---------- Contrôles ----------
cnt = collections.Counter(p['g'] for p in people)
assert cnt['an'] == 574 and cnt['sen'] == 348, cnt
assert cnt['pr'] == 1 and PR['n'] == 'Emmanuel Macron', PR['n']
assert PM['n'] == 'Sébastien Lecornu', PM['n']
assert cnt['gouv'] == 35 and cnt['vac'] == 2, cnt  # vacants : Ruralité, préfecture de l'Essonne
assert 100 <= cnt['pref'] <= 106, cnt['pref']  # décret du 26 février 2026 : PM + 35 ; départ de M. Fournier (Ruralité) annoncé le 17/09/2026
assert len({p['id'] for p in people}) == len(people)
for p in people:
    for k in [k for k, v in p.items() if v is None or v == '' or v == [] or (k == 'spec' and not v)]:  # garder rank 0 (Premier ministre)
        del p[k]
json.dump({'pp': people, 'ref': REFNAME[-13:-5]}, open(S + '/people.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump(photos, open(S + '/photos.json', 'w', encoding='utf-8'))
print('ok', dict(cnt), 'hatvp', sum(1 for p in people if p.get('ht')), 'jo', sum(1 for p in people if p.get('jo')), 'bureau', dict(qual), 'spec', sum(1 for p in people if p.get('spec')))
