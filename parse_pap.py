import re, json, sys
L = open('pap_es.txt', encoding='utf-8').read().split('\n')
a, b = int(sys.argv[1]), int(sys.argv[2])  # 1-based inclusive line range of the table
L = L[a-1:b]
isval = lambda s: s.strip()=='' or re.fullmatch(r'[-+]?[\d  ]+(,\d+)?\s*%?', s.strip()) is not None
num = lambda s: int(re.sub(r'\D','',s)) if re.sub(r'\D','',s) else 0
out, i = [], 0
while i < len(L):
    if isval(L[i]) or L[i].startswith('=====PAGE'): i += 1; continue
    lab = []
    while i < len(L) and not isval(L[i]):
        t=L[i].strip()
        if re.match(r'^\d{2,3} – ', t): lab=[t]
        elif not L[i].startswith('=====PAGE'): lab.append(t)
        i += 1
    vals = L[i:i+12]; i += 12
    label = ' '.join(lab)
    m = re.match(r"^(\d{2,3}) – (.*)$", label)
    if not m: continue
    out.append({'code': m.group(1), 'label': m.group(2), 'ae25': num(vals[0]), 'ae26': num(vals[1]), 'cp25': num(vals[6]), 'cp26': num(vals[7])})
json.dump(out, open('pap_actions.json','w',encoding='utf-8'), ensure_ascii=False, indent=0)
for o in out: print(o['code'], o['label'][:55].ljust(55), f"{o['cp25']:>15,}", f"{o['cp26']:>15,}")
