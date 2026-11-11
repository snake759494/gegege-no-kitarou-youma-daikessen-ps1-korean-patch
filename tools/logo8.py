# 타이틀 메뉴 컬러 로고(팩25 엔트리0, 8bpp) 한글화
import struct, json, os, numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont
W=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
A=0x2cb048
# 화면 ↔ 텍스처 대응 (메뉴 화면 프레임버퍼 대조로 측정)
P1=dict(tx=512,ty=-16,sx0=0,sx1=256,sy0=16,sy1=176)      # 텍스처 (sx+512, sy-16)
P2=dict(tx=264,ty=120,sx0=248,sx1=320,sy0=40,sy1=136)     # 텍스처 (sx+264, sy+120)
P3=dict(tx=336,ty=32,sx0=248,sx1=320,sy0=123,sy1=160)     # 후리가나 조각
def rgb(c): return np.stack([(c&31)<<3,((c>>5)&31)<<3,((c>>10)&31)<<3],-1).astype(float)
def apply(fad,preview=None):
    x,y,w,h=struct.unpack_from('<4H',fad,A)
    b8=np.frombuffer(bytes(fad[A+8:A+8+w*h*2]),np.uint8).reshape(h,w*2).copy()
    pal=json.load(open(os.path.join(W,'text/logo_pal.json')))
    P=np.zeros(256,int)
    for k,v in pal.items(): P[int(k)]=v
    PR=rgb(P)
    # 화면 합성(텍스처만)
    S=np.full((240,320),-1,int)
    for p in (P3,P2,P1):
        for sy in range(p['sy0'],p['sy1']):
            ty=sy+p['ty']
            if not 0<=ty<h: continue
            row=b8[ty,p['sx0']+p['tx']:p['sx1']+p['tx']].astype(int); cur=S[sy,p['sx0']:p['sx1']]
            S[sy,p['sx0']:p['sx1']]=np.where((row!=0)|(cur<0),row,cur)
    col=PR[np.clip(S,0,255)]
    r,g,b=col[...,0],col[...,1],col[...,2]
    red=(r>=72)&(g<=r*0.45)&(b<=r*0.5)
    brown=(r>=56)&(r>=g*1.35)&(r>=b*1.35)
    dark=(r+g+b<=150)&(S>0)
    box=np.zeros_like(red)
    box[50:82,84:240]=True; box[70:142,8:306]=True
    mask=box&(red|dark|brown)
    mask=ndimage.binary_closing(mask,np.ones((3,3)))&box
    mask=ndimage.binary_dilation(mask)&box
    # 글자 색 인덱스
    rv=S[mask&red]; fill=np.bincount(rv,minlength=256).argmax()
    dv=S[mask&dark]; edge=np.bincount(dv,minlength=256).argmax()
    reds=[i for i in range(1,256) if (PR[i,0]>=72 and PR[i,1]<=PR[i,0]*.45)]
    # 배경 메우기: 투명/불투명은 최근접, 색은 확산
    known=~mask&(S>=0)
    idx=ndimage.distance_transform_edt(~known,return_distances=False,return_indices=True)
    near=S[idx[0],idx[1]]
    out=S.copy(); out[mask]=near[mask]
    c=col.copy(); c[~known]=np.nan
    cc=np.where(np.isnan(c),PR[np.clip(near,0,255)],c)
    for _ in range(80):
        avg=(np.roll(cc,1,0)+np.roll(cc,-1,0)+np.roll(cc,1,1)+np.roll(cc,-1,1))/4
        cc[mask]=avg[mask]
    region=box&~mask&(S>0)
    cand=np.unique(S[region]); cand=np.array([i for i in cand if i not in reds and P[i]!=0])
    sel=mask&(out!=0)
    d=((cc[sel][:,None,:]-PR[cand][None,:,:])**2).sum(-1)
    out[sel]=cand[d.argmin(1)]
    # 한글 로고 그리기
    def draw(text,bx,font,size):
        x0,y0,x1,y1=bx; F=ImageFont.truetype(os.path.join(W,'..',font),size*4)
        bb=F.getbbox(text); im=Image.new('L',(bb[2]-bb[0]+8,bb[3]-bb[1]+8),0)
        ImageDraw.Draw(im).text((4-bb[0],4-bb[1]),text,font=F,fill=255); im=im.crop(im.getbbox())
        im=im.resize((x1-x0-4,y1-y0-4),Image.LANCZOS)
        m=np.zeros((240,320),bool); m[y0+2:y1-2,x0+2:x1-2]=np.array(im)>110
        return m
    T=draw('게게게의 기타로',(88,51,238,80),'NanumSquareNeo-eHv.ttf',28)|draw('역습! 요마대혈전',(12,79,306,130),'NanumSquareNeo-eHv.ttf',48)
    sh=np.zeros_like(T); sh[3:,2:]=T[:-3,:-2]                     # 그림자
    ring=ndimage.binary_dilation(T,np.ones((5,5)))
    out[(sh|ring)&~T]=edge
    out[T]=fill
    # 윗부분 밝은 빨강
    lighter=sorted(reds,key=lambda i:-PR[i].sum())
    hi=next((i for i in lighter if PR[i,0]>PR[fill,0]+10),fill)
    top=T&~np.roll(T,2,0); out[top]=hi
    changed=(out!=S)&(S>=0)
    for p in (P1,P2,P3):
        for sy in range(p['sy0'],p['sy1']):
            ty=sy+p['ty']
            if not 0<=ty<h: continue
            for sx in np.nonzero(changed[sy,p['sx0']:p['sx1']])[0]+p['sx0']:
                b8[ty,sx+p['tx']]=out[sy,sx]
    fad[A+8:A+8+w*h*2]=b8.tobytes()
    if preview:
        Image.fromarray(PR[np.clip(out,0,255)].astype('uint8')).resize((960,720),0).save(preview)
if __name__=='__main__':
    fad=bytearray(open(os.path.join(W,'orig/DATA.FAD'),'rb').read()); apply(fad,os.path.join(W,'zlogo.png'))
