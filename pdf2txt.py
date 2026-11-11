import sys, fitz
d = fitz.open(sys.argv[1])
with open(sys.argv[2], 'w', encoding='utf-8') as f:
    for i, p in enumerate(d):
        f.write(f'\n=====PAGE {i+1}=====\n' + p.get_text())
print(len(d))
