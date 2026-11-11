import sys, json, os, time, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
# usage: python -I dl_cv.py people.json dossier_sortie
# 1) JORFSearch : toutes les mentions de chaque personne au Journal officiel
# 2) Wikidata : fiche de la personne (études, postes), choisie sans ambiguïté
pp = [p for p in json.load(open(sys.argv[1], encoding='utf-8'))['pp'] if p['g'] != 'vac']
out = sys.argv[2]
UA = {'User-Agent': 'QuiGubernareDebet/1.0 (site citoyen; donnees publiques)'}
os.makedirs(out + '/jorf', exist_ok=True)


def get(url, data=None, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=dict(UA, **({'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/sparql-results+json'} if data else {})))
            return urllib.request.urlopen(req, timeout=120).read()
        except Exception as e:
            err = e
            time.sleep(3 * (i + 1))
    raise err


def jorf(p):
    f = out + '/jorf/' + p['id'] + '.json'
    if os.path.exists(f):
        return 0
    b = get('https://jorfsearch.steinertriples.ch/name/' + urllib.parse.quote(p['n']) + '?format=JSON')
    open(f, 'wb').write(b)
    time.sleep(0.3)
    return 1


with ThreadPoolExecutor(3) as ex:
    n = sum(ex.map(jorf, pp))
print('jorf', n, 'nouveaux sur', len(pp))

# Wikidata : 1) candidats par libellé exact
SP = 'https://query.wikidata.org/sparql'


def sparql(q):
    return json.loads(get(SP, urllib.parse.urlencode({'query': q}).encode()))['results']['bindings']


names = sorted({p['n'] for p in pp})
cand = {}
for i in range(0, len(names), 80):
    vals = ' '.join(json.dumps(x, ensure_ascii=False) + '@fr' for x in names[i:i + 80])
    q = '''SELECT ?p ?lab ?an ?sen ?b WHERE { VALUES ?lab { %s } ?p rdfs:label ?lab; wdt:P31 wd:Q5.
      OPTIONAL { ?p wdt:P4123 ?an } OPTIONAL { ?p wdt:P1808 ?sen } OPTIONAL { ?p wdt:P569 ?b } }''' % vals
    for r in sparql(q):
        c = cand.setdefault(r['lab']['value'], {}).setdefault(r['p']['value'].rsplit('/', 1)[1], {})
        for k in ('an', 'sen', 'b'):
            if k in r:
                c[k] = r[k]['value']
    time.sleep(1)
json.dump(cand, open(out + '/wd_cand.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('wikidata candidats', len(cand))
