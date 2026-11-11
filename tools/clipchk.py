# 프레임버퍼와 텍스처를 대조해 스프라이트에서 잘린 글자 픽셀 찾기
import sys,os,numpy as np
sys.path.insert(0,os.path.dirname(__file__)); import fb,gfx,gfxprev
def run(addr,items,thr=8,yr=(0,480)):
    out=fb.vram(); b=fb.base(out)
    v=np.frombuffer(out[b:b+1048576],'<u2').reshape(512,1024).astype(np.int64)
    F=v[yr[0]:yr[1],0:320]; L=(F&31)+((F>>5)&31)+((F>>10)&31)
    fad=bytearray(open(os.path.join(fb.W,'orig/DATA.FAD'),'rb').read()); gfxprev.apply(fad,addr)
    T=gfx.load(fad,addr)
    res=[]
    for name,(x0,y0,x1,y1) in items:
        t=T[y0:y1,x0:x1]>thr
        if not t.any(): continue
        best=None
        # 화면 밝기 차이(이웃 대비) 이진화로 비교
        for lim in (60,75,90):
            B=L>lim
            for dy in range(0,F.shape[0]-t.shape[0]):
                for dx in range(0,320-t.shape[1]):
                    P=B[dy:dy+t.shape[0],dx:dx+t.shape[1]]
                    s=(P&t).sum()-2*(~P&t).sum()-(P&~t).sum()
                    if best is None or s>best[0]: best=(s,dx,dy,lim)
        s,dx,dy,lim=best; P=(L>lim)[dy:dy+t.shape[0],dx:dx+t.shape[1]]
        miss=t&~P; ys,xs=np.nonzero(miss)
        res.append((name,s,int(t.sum()),dx,dy+yr[0],int(miss.sum()),(int(xs.min())+x0,int(ys.min())+y0,int(xs.max())+x0+1,int(ys.max())+y0+1) if len(xs) else None))
    for r in res: print(r)
