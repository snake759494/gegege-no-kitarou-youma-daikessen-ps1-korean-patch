# 명판(밝은 판 위 어두운 글자) 측정·교체
import numpy as np, os
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont
W=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
def plates(img,region,minarea=150):
    x0,y0,x1,y1=region; sub=img[y0:y1,x0:x1]
    p=sub>=7
    f=ndimage.binary_fill_holes(ndimage.binary_closing(p,np.ones((3,3))))
    lab,n=ndimage.label(f); out=[]
    for i,sl in enumerate(ndimage.find_objects(lab)):
        m=lab[sl]==i+1
        if m.sum()<minarea: continue
        txt=ndimage.binary_erosion(m,np.ones((5,5)))&(sub[sl]<=6)&(sub[sl]>0)
        txt=ndimage.binary_opening(txt,np.ones((1,1)))
        ys,xs=np.nonzero(txt)
        pb=(x0+sl[1].start,y0+sl[0].start,x0+sl[1].stop,y0+sl[0].stop)
        tb=(pb[0]+xs.min(),pb[1]+ys.min(),pb[0]+xs.max()+1,pb[1]+ys.max()+1) if len(xs) else None
        out.append((pb,tb))
    return sorted(out,key=lambda t:(t[0][1]//8,t[0][0]))
def font_for(text,maxw,size=None):
    for fn,sz in (('Galmuri11.ttf',12),('Galmuri9.ttf',10)):
        F=ImageFont.truetype(os.path.join(W,'fonts',fn),sz)
        if F.getlength(text)<=maxw: return F
    return F
def textmask(text,F,w,h):
    g=Image.new('L',(w,h),0); d=ImageDraw.Draw(g)
    bb=d.textbbox((0,0),text,font=F); tw,th=bb[2]-bb[0],bb[3]-bb[1]
    d.text(((w-tw)//2-bb[0],(h-th)//2-bb[1]),text,font=F,fill=255)
    return np.array(g)>127
def inpaint(sub,mask):
    # 세로 보간으로 글자 자리 메우기
    out=sub.copy().astype(float); H=sub.shape[0]
    for x in range(sub.shape[1]):
        col=mask[:,x]
        if not col.any(): continue
        good=np.nonzero(~col)[0]
        if len(good)==0: out[:,x]=np.median(sub[~mask]); continue
        out[col,x]=np.interp(np.nonzero(col)[0],good,sub[good,x].astype(float))
    return np.round(out).astype(np.uint8)
def replace(img,pb,tb,text,ink=2,thr=8,maxw=None,vertical=False,font=None,pthr=7):
    x0,y0,x1,y1=pb
    sub=img[y0:y1,x0:x1]
    plate=ndimage.binary_fill_holes(ndimage.binary_closing(sub>=pthr,np.ones((3,3))))
    m=plate&(sub<=thr)&(sub>0)
    m=ndimage.binary_dilation(m)&ndimage.binary_erosion(plate,np.ones((3,3)))
    # 판 바깥 가장자리 근처는 건드리지 않음
    tx0,ty0,tx1,ty1=tb
    inner=np.zeros_like(m); inner[max(0,ty0-y0-2):ty1-y0+2,max(0,tx0-x0-2):tx1-x0+2]=True
    m&=inner
    rng=np.random.default_rng(1)
    inner2=ndimage.binary_erosion(plate,np.ones((5,5)))
    for y in range(sub.shape[0]):
        xs=np.nonzero(m[y])[0]
        if not len(xs): continue
        pool=sub[y][inner2[y]&~m[y]&(sub[y]>=9)]
        if len(pool)<3:
            ys=slice(max(0,y-3),y+4); pool=sub[ys][inner2[ys]&~m[ys]&(sub[ys]>=9)]
        if len(pool): sub[y,xs]=rng.choice(pool,len(xs))
    if vertical:
        fn,sz=font or ('fonts/Galmuri11.ttf',12)
        F=ImageFont.truetype(os.path.join(W,fn),sz)
        n=len(text); bh=ty1-ty0; step=min(sz,bh//n)
        oy=(ty0+ty1)//2-(step*n)//2; cs=sz+2
        for i,c in enumerate(text):
            mk=textmask(c,F,cs,cs); cx=(tx0+tx1)//2-cs//2; yy=oy+i*step-1
            r=img[yy:yy+cs,cx:cx+cs]; r[mk[:r.shape[0],:r.shape[1]]]=ink
        return
    w=maxw or (x1-x0-18)
    F=font_for(text,w) if not font else ImageFont.truetype(os.path.join(W,font[0]),font[1])
    cx=(tx0+tx1)/2-x0; cy=(ty0+ty1)/2-y0
    Wd=x1-x0; P=200
    g=Image.new('L',(Wd+2*P,y1-y0),0); d=ImageDraw.Draw(g)
    bb=d.textbbox((0,0),text,font=F)
    d.text((round(P+cx-(bb[0]+bb[2])/2),round(cy-(bb[1]+bb[3])/2)),text,font=F,fill=255)
    big=np.array(g)>127
    xs=np.nonzero(big.any(0))[0]
    if xs[-1]-xs[0]+1>w:
        part=big[:,xs[0]:xs[-1]+1]; idx=np.round(np.linspace(0,part.shape[1]-1,w)).astype(int)
        big=np.zeros_like(big); c0=int(round(P+cx-w/2)); big[:,c0:c0+w]=part[:,idx]
    mk=big[:,P:P+Wd]
    sub[mk&plate]=ink

def black(img,box,text,ink=15,align='l',maxw=None,dy=0,extra=0):
    x0,y0,x1,y1=box; img[y0:y1,x0:x1]=0
    if not text: return
    w=maxw or (x1-x0+extra)
    F=font_for(text,w)
    H=y1-y0; P=300
    g=Image.new('L',(w+2*P,H),0); d=ImageDraw.Draw(g)
    bb=d.textbbox((0,0),text,font=F)
    d.text((P-bb[0],round(min(14,H)/2-(bb[1]+bb[3])/2)+dy),text,font=F,fill=255)
    big=np.array(g)>127; xs=np.nonzero(big.any(0))[0]
    part=big[:,xs[0]:xs[-1]+1]
    if part.shape[1]>w:
        idx=np.round(np.linspace(0,part.shape[1]-1,w)).astype(int); part=part[:,idx]
    ox=0 if align=='l' else ((w-part.shape[1]) if align=='r' else (w-part.shape[1])//2)
    r=img[y0:y1,x0+ox:x0+ox+part.shape[1]]
    r[part[:r.shape[0],:r.shape[1]]]=ink

def vblack(img,box,text,ink=15,font=('fonts/Galmuri11.ttf',12),clear=True):
    x0,y0,x1,y1=box
    if clear: img[y0:y1,x0:x1]=0
    F=ImageFont.truetype(os.path.join(W,font[0]),font[1]); sz=font[1]
    n=len(text); step=min(sz+1,(y1-y0)//n); oy=y0+((y1-y0)-step*n)//2
    for i,c in enumerate(text):
        g=Image.new('L',(x1-x0,step+2),0); d=ImageDraw.Draw(g); bb=d.textbbox((0,0),c,font=F)
        if c in '「」':  # 세로쓰기 괄호
            g2=Image.new('L',(sz+2,sz+2),0); ImageDraw.Draw(g2).text((1,1),c,font=F,fill=255); g2=g2.rotate(-90)
            g.paste(g2.crop((0,0,min(g.width,g2.width),min(g.height,g2.height))),((g.width-g2.width)//2,0))
        else:
            d.text(((x1-x0)/2-(bb[0]+bb[2])/2,(step+2)/2-(bb[1]+bb[3])/2),c,font=F,fill=255)
        m=np.array(g)>127; yy=oy+i*step-1
        r=img[yy:yy+step+2,x0:x1]; r[m[:r.shape[0],:r.shape[1]]]=ink
