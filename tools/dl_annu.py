import sys, json, urllib.request, urllib.parse, collections
# usage: python -I dl_annu.py <filtre where ODSQL> <fichier sortie> — toutes les fiches de l'annuaire local qui répondent au filtre
where, out = sys.argv[1], sys.argv[2]
base = 'https://api-lannuaire.service-public.fr/api/explore/v2.1/catalog/datasets/api-lannuaire-administration/records'
rows, off = [], 0
while True:
    q = urllib.parse.urlencode({'where': where, 'limit': 100, 'offset': off})
    req = urllib.request.Request(base + '?' + q, headers={'User-Agent': 'Mozilla/5.0 (site citoyen)'})
    d = json.load(urllib.request.urlopen(req, timeout=120))
    rows += d['results']
    off += 100
    if off >= d['total_count'] or not d['results']:
        break
json.dump(rows, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
types = collections.Counter(t['type_service_local'] for r in rows for t in json.loads(r['pivot'] or '[]'))
print(len(rows), types.most_common(15))
