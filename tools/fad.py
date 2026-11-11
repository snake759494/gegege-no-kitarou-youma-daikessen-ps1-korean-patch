import struct
def parse(b,s):
    if s+12>len(b): return None
    hs=struct.unpack_from('<I',b,s)[0]
    if hs%12 or hs<24 or hs>0x1000: return None
    n=hs//12; ents=[]
    for i in range(n):
        o,t,z=struct.unpack_from('<3I',b,s+i*12)
        if o==0 and z==0: break
        ents.append((o,t,z))
    if not ents or ents[0][0]!=hs: return None
    for i in range(len(ents)-1):
        if ents[i][0]+ents[i][2]!=ents[i+1][0]: return None
    return ents
def packs(b):
    res=[]
    for s in range(0,len(b),2048):
        e=parse(b,s)
        if e: res.append((s,e))
    return res
if __name__=='__main__':
    b=open('orig/DATA.FAD','rb').read()
    P=packs(b)
    import collections
    c=collections.Counter()
    for s,e in P:
        for o,t,z in e: c[t]+=1
    print(len(P)); print(sorted((hex(k),v) for k,v in c.items()))
    for i,(s,e) in enumerate(P):
        end=s+e[-1][0]+e[-1][2]
        nxt=P[i+1][0] if i+1<len(P) else len(b)
        print(i,hex(s),len(e),'end',hex(end),'next',hex(nxt),' '.join('%x'%t for o,t,z in e))
