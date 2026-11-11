import sys, json, os, urllib.request, concurrent.futures as cf
# usage: python -I dl_photos.py photos.json dossier_sortie
items, out = json.load(open(sys.argv[1])), sys.argv[2]


def get(it):
    g, pid, url = it
    dst = os.path.join(out, g, pid + '.jpg')
    if os.path.exists(dst) and os.path.getsize(dst) > 1000:
        return pid, 'ok'
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (site citoyen)'})
        with urllib.request.urlopen(req, timeout=60) as r:
            b = r.read()
        if b[:3] != b'\xff\xd8\xff':
            return pid, 'pas une image'
        open(dst, 'wb').write(b)
        return pid, 'ok'
    except Exception as e:
        return pid, str(e)[:80]


with cf.ThreadPoolExecutor(4) as ex:
    res = list(ex.map(get, items))
bad = [r for r in res if r[1] != 'ok']
print('ok', len(res) - len(bad), 'echecs', len(bad))
for b in bad[:30]:
    print(b)
