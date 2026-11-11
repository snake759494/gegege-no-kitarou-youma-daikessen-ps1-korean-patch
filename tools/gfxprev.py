import sys,os,importlib.util
sys.path.insert(0,os.path.dirname(__file__)); import gfx, plate
import numpy as np
W=os.path.join(os.path.dirname(__file__),'..')
spec=importlib.util.spec_from_file_location('gs',os.path.join(W,'text/gfx_spec.py')); gs=importlib.util.module_from_spec(spec); spec.loader.exec_module(gs)
_R=None
_O={}
def _orig(a):
    if a not in _O: _O[a]=gfx.load(open(os.path.join(W,'orig/DATA.FAD'),'rb').read(),a)
    return _O[a]
def rect_of(a,box):
    fit(a,box); return _LAST
_LAST=None
def fit(a,box,tag=''):
    # 원래 글자 상자를 실제 스프라이트 사각형 안으로 (여백 1px)
    global _R,_LAST
    _LAST=None
    if _R is None:
        import sprites; _R=sprites.load()
    x0,y0,x1,y1=box; A=(x1-x0)*(y1-y0); best=None
    for r in _R.get(a,()):
        ix=max(0,min(x1,r[2])-max(x0,r[0])); iy=max(0,min(y1,r[3])-max(y0,r[1]))
        if ix*iy>=0.7*A:
            ar=(r[2]-r[0])*(r[3]-r[1])
            if best is None or ar<best[0]: best=(ar,r)
    if not best:
        # 표가 없으면 원본 글자 잉크 범위 안으로 제한
        o=_orig(a); m=o[y0:y1,x0:x1]>3
        if not m.any(): return box
        import numpy as _n; ys,xs=_n.nonzero(m)
        nb=(x0+xs.min(),y0+ys.min(),x0+xs.max()+1,y0+ys.max()+1)
        if nb!=tuple(box) and os.environ.get('FITLOG'): print('ink',hex(a),tag,box,'->',nb)
        return nb
    r=best[1]; _LAST=r[:4]; nb=(max(x0,r[0]+1),max(y0,r[1]+1),min(x1,r[2]-1),min(y1,r[3]-1))
    if nb!=tuple(box) and os.environ.get('FITLOG'): print('fit',hex(a),tag,box,'->',nb,'rect',r[:4])
    return nb
def apply(fad,only=None):
    keys=set(gs.SPEC)|set(getattr(gs,'AUTO',{}))|set(getattr(gs,'PLATES',{}))|set(getattr(gs,'BLACK',{}))|set(getattr(gs,'ICONS',{}))|set(getattr(gs,'VBLACK',{}))
    for a in sorted(keys):
        items=gs.SPEC.get(a,[])
        if only and a!=only: continue
        img=gfx.load(fad,a)
        for w_ in getattr(gs,'WIPE',{}).get(a,[]): img[w_[1]:w_[3],w_[0]:w_[2]]=(w_[4] if len(w_)>4 else 0)
        for box,text,opt in items:
            box=fit(a,box,text)
            o=dict(opt); font=os.path.join(W,'..',o.pop('font',gs.HV)) if not o.get('fontpath') else o.pop('fontpath')
            size=o.pop('size',24); clear=o.pop('clear',0)
            inv=o.pop('inv',False)
            arr=gfx.render(text,font,size,box,**o)
            if inv: arr[arr>=0]=16-arr[arr>=0]
            gfx.paste(img,box,arr,clear=clear)
        for (tx,ty,ch) in getattr(gs,'ICONS',{}).get(a,[]):
            img[ty+3:ty+17,tx+2:tx+22]=img[211:225,34:54]
            F=gfx.ImageFont.truetype(os.path.join(W,'fonts/Galmuri11.ttf'),12)
            g=gfx.Image.new('L',(20,14),0); gfx.ImageDraw.Draw(g).text((4,1),ch,font=F,fill=255)
            m=np.array(g)>127; sub=img[ty+3:ty+17,tx+2:tx+22]; sub[m]=1
        if a in getattr(gs,'AUTO',{}):
            reg,texts=gs.AUTO[a]; P=plate.plates(img,reg)
            assert len(P)==len(texts),(hex(a),len(P),len(texts))
            for (pb,tb),t in zip(P,texts):
                if t: plate.replace(img,pb,fit(a,tuple(int(q) for q in tb),t),t)
        for it in getattr(gs,'PLATES',{}).get(a,[]):
            pb,tb,text=it[:3]; o=it[3] if len(it)>3 else {}
            plate.replace(img,pb,fit(a,tb,text),text,**o)
        for it in getattr(gs,'BLACK',{}).get(a,[]):
            nb=fit(a,it[0],it[1]); r=_LAST
            if r: img[r[1]:r[3],r[0]:r[2]]=0
            plate.black(img,nb,it[1],**(it[2] if len(it)>2 else {}))
        for it in getattr(gs,'VBLACK',{}).get(a,[]):
            plate.vblack(img,fit(a,it[0],it[1]),it[1],**(it[2] if len(it)>2 else {}))
        gfx.store(fad,a,img)
if __name__=='__main__':
    fad=bytearray(open(os.path.join(W,'orig/DATA.FAD'),'rb').read())
    a=int(sys.argv[1],16); R=tuple(int(v) for v in sys.argv[2].split(','))
    apply(fad,a); img=gfx.load(fad,a)
    gfx.show(img,R,[],sys.argv[3] if len(sys.argv)>3 else 'survey/prev.png')
