import sys,json;sys.path.insert(0,'tools')
from ko import load
ko=load();B=json.load(open('text/ja.json',encoding='utf-8'))
def ssize(s): n=len(s.replace('/','\n\n'))*2- s.count('/')*2+2; return (n+3)&~3  # '/'→2바이트
for i,bl in enumerate(B):
    if 'strs' not in bl: continue
    n=len(bl['strs']); tot=4*n+sum(ssize(ko[(i,j)]) for j in range(n))
    if tot>bl['size']: print('B%d'%i,hex(tot),hex(bl['size']),tot-bl['size'],[ (j,ssize(ko[(i,j)])%4==0 and len(ko[(i,j)].replace('/','x'))*2+2) for j in range(n)][:0])
