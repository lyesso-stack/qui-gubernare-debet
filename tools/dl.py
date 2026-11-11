import sys, urllib.request, os
# usage: python -I dl.py <url> <fichier_sortie>
url, out = sys.argv[1], sys.argv[2]
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (site citoyen)'})
with urllib.request.urlopen(req, timeout=120) as r, open(out, 'wb') as f:
    f.write(r.read())
print(out, os.path.getsize(out))
