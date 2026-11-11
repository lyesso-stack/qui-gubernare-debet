import sys, json, urllib.request, urllib.parse, collections
# usage: python -I dl_pref.py dossier_sortie — toutes les fiches de l'annuaire local dont le type contient « prefecture »
out = sys.argv[1]
base = 'https://api-lannuaire.service-public.fr/api/explore/v2.1/catalog/datasets/api-lannuaire-administration/records'
rows, off = [], 0
while True:
    q = urllib.parse.urlencode({'where': 'search(pivot,"prefecture")', 'limit': 100, 'offset': off})
    req = urllib.request.Request(base + '?' + q, headers={'User-Agent': 'Mozilla/5.0 (site citoyen)'})
    d = json.load(urllib.request.urlopen(req, timeout=120))
    rows += d['results']
    off += 100
    if off >= d['total_count']:
        break
json.dump(rows, open(out + '/prefectures.json', 'w', encoding='utf-8'), ensure_ascii=False)
types = collections.Counter(t['type_service_local'] for r in rows for t in json.loads(r['pivot'] or '[]'))
print(len(rows), types.most_common(12))
pref = [r for r in rows if any(t['type_service_local'] == 'prefecture' for t in json.loads(r['pivot'] or '[]'))]
print('prefecture', len(pref), 'avec personne', sum(1 for r in pref if r['affectation_personne']))
if pref:
    r = pref[0]
    print(r['nom'], '|', r['affectation_personne'][:600] if r['affectation_personne'] else None, '|', r['url_service_public'] if 'url_service_public' in r else '')
