# 팩의 type 5 스프라이트 표 → 각 이미지(type 0)의 텍스처 좌표 사각형
import struct,sys,os
sys.path.insert(0,os.path.dirname(__file__)); from fad import packs
W=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
def load():
    fad=open(os.path.join(W,'orig/DATA.FAD'),'rb').read()
    rects={}; G={}
    P=packs(fad)
    for o,t,z in P[0][1]:
        a=P[0][0]+o
        if t==0 and z>16: G[a]=struct.unpack_from('<4H',fad,a)
    for s,ents in P:
      imgs=dict(G); tabs=[]
      for o,t,z in ents:
            a=s+o
            if t==0 and z>16:
                x,y,w,h=struct.unpack_from('<4H',fad,a)
                if w and h and w*h*2+8<=z+8: imgs[a]=(x,y,w,h)
            if t==5: tabs.append((a,z))
      for a,z in tabs:
        d=fad[a:a+z]
        for k in range(0,len(d)-16,4):
            tp,cl,u,v,w,h,x,y=struct.unpack_from('<HHHHHHhh',d,k)
            if tp>=0x200 or not(0<w<=256 and 0<h<=256 and u<256 and v<256): continue
            if (cl>>8) not in range(0x40,0x80): continue
            dep=(tp>>7)&3
            if dep>1: continue
            px=(tp&15)*64; py=((tp>>4)&1)*256
            per=4 if dep==0 else 2
            for ia,(ix,iy,iw,ih) in imgs.items():
                vx=px+u//per; vy=py+v
                if ix<=vx<ix+iw and iy<=vy<iy+ih:
                    tx=(px-ix)*per+u; ty=py-iy+v
                    rects.setdefault(ia,set()).add((tx,ty,tx+w,ty+h,dep))
    return rects
if __name__=='__main__':
    R=load()
    for a in map(lambda s:int(s,16),sys.argv[1:]):
        for r in sorted(R.get(a,()),key=lambda r:(r[1],r[0])): print(hex(a),r)
