import struct,sys,json,os
sys.path.insert(0,os.path.dirname(__file__)); from fad import packs
b=open('orig/DATA.FAD','rb').read()
P=packs(b)
blocks=[];seen={}
for pi,(s,e) in enumerate(P):
    for ei,(o,t,z) in enumerate(e):
        if t!=0x14: continue
        d=b[s+o:s+o+z]
        n=struct.unpack_from('<I',d,0)[0]//4
        offs=struct.unpack_from('<%dI'%n,d,0)
        strs=[]
        for k in offs:
            j=d.index(b'\0',k)
            strs.append(d[k:j].decode('cp932'))
        key=tuple(strs)
        blocks.append({'pack':pi,'ent':ei,'abs':s+o,'size':z,'dup':seen.get(key)})
        if key not in seen: seen[key]=len(blocks)-1; blocks[-1]['strs']=strs
json.dump(blocks,open('text/ja.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
# raw control check
bad=set()
for bl in blocks:
    for s_ in bl.get('strs',[]):
        for c in s_:
            if ord(c)<0x20 and c!='\n': bad.add(c)
print(len(blocks),sum(1 for x in blocks if x['dup'] is None),bad)
