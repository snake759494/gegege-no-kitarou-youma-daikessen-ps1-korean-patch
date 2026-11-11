import json,glob,os
D=os.path.join(os.path.dirname(__file__),'..','text')
def load():
    ko={}
    for f in sorted(glob.glob(D+'/ko_*.tsv')):
        for ln in open(f,encoding='utf-8'):
            ln=ln.rstrip('\n')
            if not ln: continue
            b,j,t=ln.split('\t')
            ko[(int(b[1:]),int(j))]=t
    return ko
N1=' ,.!'
N2='?0123456789'
def adv(c):
    return 4 if c in N1 else 8 if c in N2 else 12
def width(line):
    return sum(adv(c) for c in line)
