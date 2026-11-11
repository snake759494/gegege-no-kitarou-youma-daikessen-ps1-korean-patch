# 세이브스테이트(슬롯1)에서 VRAM 추출 → 프레임버퍼 PNG (1:1)
import zstandard,struct,numpy as np,sys,os,time
from PIL import Image
W=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
def vram():
    d=open(os.path.join(W,'duck/savestates/SLPM-87286_1.sav'),'rb').read()
    dc=zstandard.ZstdDecompressor(); out=b''; k=d.find(b'\x28\xb5\x2f\xfd')
    while k>=0:
        try: out+=dc.decompressobj().decompress(d[k:])
        except Exception: pass
        k=d.find(b'\x28\xb5\x2f\xfd',k+4)
    # VRAM 1MB: 상태 안 위치는 고정 — 마지막에 찾은 위치 사용
    return out
def save(out,base,png,scale=3):
    v=np.frombuffer(out[base:base+1048576],'<u2').reshape(512,1024)
    ims=[]
    for y0 in (0,240):
        c=v[y0:y0+240,0:320]; ims.append(np.dstack([(c&31)<<3,((c>>5)&31)<<3,((c>>10)&31)<<3]).astype('uint8'))
    im=Image.fromarray(np.vstack(ims)); im.resize((im.width*scale,im.height*scale),0).save(png)
def base(out):
    exe=open(os.path.join(W,'orig/SLPM_872.86'),'rb').read()
    return out.find(exe[0x900:0x940])-0x20100+2098161
if __name__=='__main__':
    out=vram(); b=base(out); print(b); save(out,b,sys.argv[1])
