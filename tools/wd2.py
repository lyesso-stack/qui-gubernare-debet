import sys, json, re, time, urllib.request, urllib.parse
# usage: python -I wd2.py people.json dl_cv -> dl_cv/wd_info.json
# Choisit la fiche Wikidata de chaque personne sans ambiguïté, puis lit naissance, description, études et postes.
pp = [p for p in json.load(open(sys.argv[1], encoding='utf-8'))['pp'] if p['g'] != 'vac']
out = sys.argv[2]
cand = json.load(open(out + '/wd_cand.json', encoding='utf-8'))
UA = {'User-Agent': 'QuiGubernareDebet/1.0 (site citoyen; donnees publiques)', 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/sparql-results+json'}


def sparql(q):
    for i in range(4):
        try:
            req = urllib.request.Request('https://query.wikidata.org/sparql', data=urllib.parse.urlencode({'query': q}).encode(), headers=UA)
            return json.loads(urllib.request.urlopen(req, timeout=120).read())['results']['bindings']
        except Exception as e:
            err = e
            time.sleep(5 * (i + 1))
    raise err


def batched(ids, q, n=150):
    rows = []
    for i in range(0, len(ids), n):
        rows += sparql(q % ' '.join('wd:' + x for x in ids[i:i + n]))
        time.sleep(1)
    return rows


# 1) descriptions des candidats hors parlementaires
others = sorted({q for p in pp if p['g'] not in ('an', 'sen') for q in cand.get(p['n'], {})})
desc = {}
for r in batched(others, 'SELECT ?p ?d WHERE { VALUES ?p { %s } OPTIONAL { ?p schema:description ?d FILTER(lang(?d)="fr") } }'):
    desc[r['p']['value'].rsplit('/', 1)[1]] = r.get('d', {}).get('value', '')
PUBLIC = re.compile(r"préf|fonctionnaire|politi|ministr|recteur|rectrice|magistrat|administrat|diplomat|universitaire|économiste|juriste|haut[ -]|militaire|officier|général|syndicaliste|chef d'entreprise|dirigeant|ingénieur|avocat|médecin", re.I)

pick = {}
for p in pp:
    c = cand.get(p['n'], {})
    if p['g'] == 'an':
        q = [k for k, v in c.items() if v.get('an', '').lstrip('PA') == p['id'].lstrip('PA')]
    elif p['g'] == 'sen':
        slug = (p.get('page') or '').rsplit('/', 1)[-1].replace('.html', '')
        q = [k for k, v in c.items() if v.get('sen') == slug]
    else:
        q = [k for k in c if PUBLIC.search(desc.get(k, ''))]
    if len(q) == 1:
        pick[p['id']] = q[0]
print('fiches sures', len(pick), 'sur', len(pp))

# 2) détails des fiches retenues
qs = sorted(set(pick.values()))
info = {q: {'b': '', 'd': '', 'e': [], 'pos': []} for q in qs}
for r in batched(qs, 'SELECT ?p ?b ?d WHERE { VALUES ?p { %s } OPTIONAL { ?p wdt:P569 ?b } OPTIONAL { ?p schema:description ?d FILTER(lang(?d)="fr") } }'):
    i = info[r['p']['value'].rsplit('/', 1)[1]]
    i['b'] = i['b'] or r.get('b', {}).get('value', '')[:4]
    i['d'] = i['d'] or r.get('d', {}).get('value', '')
for r in batched(qs, 'SELECT ?p ?el WHERE { VALUES ?p { %s } ?p wdt:P69 ?e. ?e rdfs:label ?el FILTER(lang(?el)="fr") }'):
    i = info[r['p']['value'].rsplit('/', 1)[1]]
    if r['el']['value'] not in i['e']:
        i['e'].append(r['el']['value'])
for r in batched(qs, '''SELECT ?p ?pl ?s ?f WHERE { VALUES ?p { %s } ?p p:P39 ?st. ?st ps:P39 ?x. ?x rdfs:label ?pl FILTER(lang(?pl)="fr")
      OPTIONAL { ?st pq:P580 ?s } OPTIONAL { ?st pq:P582 ?f } }''', 80):
    i = info[r['p']['value'].rsplit('/', 1)[1]]
    row = [r['pl']['value'], r.get('s', {}).get('value', '')[:4], r.get('f', {}).get('value', '')[:4]]
    if row not in i['pos']:
        i['pos'].append(row)
res = {}
for pid, q in pick.items():
    i = info[q]
    i['pos'].sort(key=lambda r: r[1] or '0', reverse=True)
    res[pid] = [q, i['b'], i['d'], i['e'][:6], i['pos'][:20]]
json.dump(res, open(out + '/wd_info.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('wd_info', len(res))
